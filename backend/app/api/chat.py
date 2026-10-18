import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.app.schemas.chat import ChatRequest, ChatResponse, LatencySchema
from backend.app.models.database import get_db
from backend.app.services.conversation import get_conversation_manager
from backend.app.rag.context_builder import ContextBuilder
from backend.app.rag.prompts import build_rag_prompt
from backend.app.llm import get_llm_provider
from backend.app.constraints.validator import ConstraintValidator

router = APIRouter(prefix="/api", tags=["Chat"])

# Singletons will be injected by main app state
def get_retrievers_from_app(request):
    return request.app.state.kw_retriever, request.app.state.dense_retriever, request.app.state.hybrid_retriever

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    session_id = req.conversation_id or "default_session"
    conv_manager = get_conversation_manager()
    session = conv_manager.get_or_create_session(session_id)

    from backend.app.main import app_state
    kw_ret = app_state.get("kw_retriever")
    dense_ret = app_state.get("dense_retriever")
    hybrid_ret = app_state.get("hybrid_retriever")

    if not kw_ret or not dense_ret or not hybrid_ret:
        raise HTTPException(status_code=503, detail="Retrieval engines are still initializing.")

    approach = req.retrieval_method.lower().strip()
    top_k = req.top_k or 5

    start_total = time.time()
    
    # Execute selected retrieval approach
    if approach == "keyword":
        retrieved_items, ret_meta = kw_ret.retrieve(query, top_k=top_k)
        method_name = "Keyword Retrieval (BM25)"
        constraints_dict = {}
        constraints_summary = ""
    elif approach == "dense":
        retrieved_items, ret_meta = dense_ret.retrieve(query, top_k=top_k)
        method_name = "Conventional Dense RAG"
        constraints_dict = {}
        constraints_summary = ""
    else:  # default hybrid
        retrieved_items, ret_meta = hybrid_ret.retrieve(query, top_k=top_k, session_context={"last_constraints": session.last_constraints})
        method_name = "Constraint-Aware Hybrid RAG"
        constraints_dict = ret_meta.get("extracted_constraints", {})
        constraints_summary = str(ret_meta.get("constraints_summary", ""))

    retrieval_latency = ret_meta.get("latency_ms", 0.0)

    # Context Construction & LLM Generation
    gen_start = time.time()
    context_str = ContextBuilder.build_context(retrieved_items)
    prompt = build_rag_prompt(query, context_str, method_name, constraints_summary)

    llm = get_llm_provider()
    answer = llm.generate_response(prompt)
    gen_latency = (time.time() - gen_start) * 1000.0

    total_latency = (time.time() - start_total) * 1000.0

    # Record conversation history
    conv_manager.record_turn(
        session_id=session_id,
        query=query,
        answer=answer,
        approach=approach
    )

    return ChatResponse(
        answer=answer,
        retrieval_method=approach,
        retrieved_items=retrieved_items,
        constraints=constraints_dict,
        latency=LatencySchema(
            retrieval_latency_ms=round(retrieval_latency, 2),
            generation_latency_ms=round(gen_latency, 2),
            total_latency_ms=round(total_latency, 2)
        ),
        metadata=ret_meta
    )
