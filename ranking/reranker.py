"""
Constraint-Aware Reranker for RestroBot.
Calculates composite relevance score using formula:
Final Score = Alpha * Semantic + Beta * Constraint + Gamma * Metadata
"""

import pandas as pd
import config


class Reranker:
    def __init__(
        self,
        alpha: float = config.WEIGHT_ALPHA,
        beta: float = config.WEIGHT_BETA,
        gamma: float = config.WEIGHT_GAMMA,
    ):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def calculate_constraint_satisfaction_score(self, item: dict, constraints: dict) -> float:
        """
        Scores how well an item satisfies active constraints (0.0 to 1.0).
        """
        checks = 0
        passed = 0

        # Max Price
        if constraints.get("max_price") is not None:
            checks += 1
            if item.get("price", 0.0) <= constraints["max_price"]:
                passed += 1

        # Min Price
        if constraints.get("min_price") is not None:
            checks += 1
            if item.get("price", 0.0) >= constraints["min_price"]:
                passed += 1

        # Diet
        if constraints.get("diet") is not None:
            checks += 1
            item_diet = str(item.get("diet", "")).lower()
            req_diet = str(constraints["diet"]).lower()
            if item_diet == req_diet:
                passed += 1

        # Spice Level
        if constraints.get("spice_level") is not None:
            checks += 1
            item_spice = str(item.get("spice_level", "")).lower()
            req_spice = str(constraints["spice_level"]).lower()
            if item_spice == req_spice:
                passed += 1

        # Restaurant
        if constraints.get("restaurant") is not None:
            checks += 1
            item_rest = str(item.get("restaurant_name", "")).lower()
            req_rest = str(constraints["restaurant"]).lower()
            if req_rest in item_rest:
                passed += 1

        # Food Type
        if constraints.get("food_type") is not None:
            checks += 1
            item_name = str(item.get("item_name", "")).lower()
            item_cat = str(item.get("menu_category", "")).lower()
            req_ft = str(constraints["food_type"]).lower()
            if req_ft in item_name or req_ft in item_cat:
                passed += 1

        if checks == 0:
            return 1.0  # No constraints requested
        return float(passed) / float(checks)

    def calculate_metadata_score(self, item: dict, constraints: dict) -> float:
        """
        Scores metadata completeness and location alignment.
        """
        score = 0.5
        if constraints.get("location"):
            req_loc = str(constraints["location"]).lower()
            item_loc = str(item.get("location", "")).lower()
            if "katpadi" in req_loc and "katpadi" in item_loc:
                score += 0.5
            elif "vellore" in req_loc and "vellore" in item_loc:
                score += 0.3
        else:
            score += 0.3
        return min(score, 1.0)

    def rerank(self, candidate_items: list[dict], constraints: dict) -> list[dict]:
        """
        Reranks candidates using the weighted composite scoring formula.
        """
        reranked = []
        for item in candidate_items:
            semantic_score = item.get("score", 0.5)
            constraint_score = self.calculate_constraint_satisfaction_score(item, constraints)
            metadata_score = self.calculate_metadata_score(item, constraints)

            final_score = (
                self.alpha * semantic_score +
                self.beta * constraint_score +
                self.gamma * metadata_score
            )

            item_copy = dict(item)
            item_copy["semantic_score"] = round(semantic_score, 4)
            item_copy["constraint_score"] = round(constraint_score, 4)
            item_copy["metadata_score"] = round(metadata_score, 4)
            item_copy["final_score"] = round(final_score, 4)
            reranked.append(item_copy)

        reranked.sort(key=lambda x: x["final_score"], reverse=True)
        return reranked
