import time
from fastapi import APIRouter, HTTPException
from backend.app.schemas.chat import CompareRequest, CompareResponse, SingleApproachResult
from backend.app.rag.context_builder import ContextBuilder
from backend.app.rag.prompts import build_rag_prompt
from backend.app.llm import get_llm_provider
from backend.app.constraints.validator import ConstraintValidator
from backend.app.constraints.extractor import ConstraintExtractor

router = APIRouter(prefix="/api", tags=["Compare"])

@router.post("/compare", response_model=CompareResponse)
def compare_endpoint(req: CompareRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    from backend.app.main import app_state
    kw_ret = app_state.get("kw_retriever")
    dense_ret = app_state.get("dense_retriever")
    hybrid_ret = app_state.get("hybrid_retriever")

    if not kw_ret or not dense_ret or not hybrid_ret:
        raise HTTPException(status_code=503, detail="Retrieval engines are still initializing.")

    top_k = req.top_k or 5
    llm = get_llm_provider()
    extracted_constraints = ConstraintExtractor.extract(query)

    # Helper function to run single pipeline
    def run_pipeline(retrievers_obj, approach_name):
        start_t = time.time()
        items, meta = retrievers_obj.retrieve(query, top_k=top_k)
        ret_latency = meta.get("latency_ms", (time.time() - start_t) * 1000.0)

        # Compute constraint satisfaction rate for retrieved set
        valid_items = 0
        for item in items:
            is_val, _, _ = ConstraintValidator.validate(item, extracted_constraints)
            if is_val:
                valid_items += 1
        csr = (valid_items / len(items)) if items else 1.0

        gen_start = time.time()
        c_summary = str(meta.get("constraints_summary", "")) if approach_name == "Constraint-Aware Hybrid RAG" else ""
        context_str = ContextBuilder.build_context(items)
        prompt = build_rag_prompt(query, context_str, approach_name, c_summary)
        answer = llm.generate_response(prompt)
        gen_latency = (time.time() - gen_start) * 1000.0

        scores = [float(item.get("retrieval_score", 0.0)) for item in items]
        return SingleApproachResult(
            answer=answer,
            retrieved_items=items,
            scores=scores,
            latency_ms=round(ret_latency, 2),
            generation_latency_ms=round(gen_latency, 2),
            constraint_satisfaction_rate=round(csr, 4),
            constraints_summary=meta.get("extracted_constraints")
        )

    # Run all 3 retrieval pipelines on the EXACT SAME query
    kw_res = run_pipeline(kw_ret, "Keyword Retrieval (BM25)")
    dense_res = run_pipeline(dense_ret, "Conventional Dense RAG")
    hybrid_res = run_pipeline(hybrid_ret, "Constraint-Aware Hybrid RAG")

    # Generate comparative summary
    comparison_summary = {
        "query": query,
        "constraints_extracted": extracted_constraints.dict_summary(),
        "keyword_latency_ms": kw_res.latency_ms,
        "dense_latency_ms": dense_res.latency_ms,
        "hybrid_latency_ms": hybrid_res.latency_ms,
        "keyword_csr": kw_res.constraint_satisfaction_rate,
        "dense_csr": dense_res.constraint_satisfaction_rate,
        "hybrid_csr": hybrid_res.constraint_satisfaction_rate,
        "recommended_approach": "Constraint-Aware Hybrid RAG" if hybrid_res.constraint_satisfaction_rate >= max(kw_res.constraint_satisfaction_rate, dense_res.constraint_satisfaction_rate) else "Conventional Dense RAG"
    }

    return CompareResponse(
        query=query,
        conversation_id=req.conversation_id or "default_session",
        keyword=kw_res,
        dense_rag=dense_res,
        hybrid_rag=hybrid_res,
        comparison_summary=comparison_summary
    )
