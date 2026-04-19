#!/usr/bin/env python3
"""Estimate token-based AI inference spend for enterprise models."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
import argparse

@dataclass(frozen=True)
class ModelCost:
    prompt_per_1k: float
    completion_per_1k: float
    description: str

MODEL_CATALOG: Mapping[str, ModelCost] = {
    "GPT-4o": ModelCost(
        prompt_per_1k=0.003,
        completion_per_1k=0.006,
        description="High-throughput reasoning and deterministic orchestration.",
    ),
    "Claude 3.5": ModelCost(
        prompt_per_1k=0.0025,
        completion_per_1k=0.005,
        description="Enterprise conversational workflows with safety and style consistency.",
    ),
    "Llama 3": ModelCost(
        prompt_per_1k=0.0015,
        completion_per_1k=0.004,
        description="Private or on-prem inference with strong cost control.",
    ),
}


def cost_per_inference(prompt_tokens: int, completion_tokens: int, model_cost: ModelCost) -> float:
    """Compute the cost of a single inference in USD."""
    prompt_cost = prompt_tokens * model_cost.prompt_per_1k / 1000
    completion_cost = completion_tokens * model_cost.completion_per_1k / 1000
    return prompt_cost + completion_cost


def estimate_monthly_cost(
    prompt_tokens: int,
    completion_tokens: int,
    rps: float,
    active_hours_per_day: float,
    active_days_per_month: int,
    model_cost: ModelCost,
    cache_hit_rate: float = 0.0,
    cache_cost_per_request: float = 0.0,
) -> dict[str, float]:
    """Estimate monthly API spend including cache efficiency."""
    assert 0.0 <= cache_hit_rate <= 1.0, "cache_hit_rate must be between 0 and 1"
    cost_one = cost_per_inference(prompt_tokens, completion_tokens, model_cost)
    requests_per_month = rps * 3600 * active_hours_per_day * active_days_per_month
    raw_monthly_cost = cost_one * requests_per_month
    effective_raw_cost = raw_monthly_cost * (1.0 - cache_hit_rate)
    cache_monthly_cost = cache_cost_per_request * requests_per_month
    effective_monthly_cost = effective_raw_cost + cache_monthly_cost
    return {
        "cost_per_inference": cost_one,
        "requests_per_month": requests_per_month,
        "raw_monthly_cost": raw_monthly_cost,
        "effective_monthly_cost": effective_monthly_cost,
        "cache_monthly_cost": cache_monthly_cost,
    }


def format_usd(value: float) -> str:
    return f"${value:,.2f}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Estimate monthly token-based AI inference costs for enterprise models."
    )
    parser.add_argument("--model", choices=MODEL_CATALOG.keys(), required=True)
    parser.add_argument("--prompt-tokens", type=int, default=1000)
    parser.add_argument("--completion-tokens", type=int, default=500)
    parser.add_argument("--rps", type=float, default=1.0)
    parser.add_argument("--active-hours", type=float, default=24.0)
    parser.add_argument("--active-days", type=int, default=22)
    parser.add_argument("--cache-hit-rate", type=float, default=0.0)
    parser.add_argument("--cache-cost-per-request", type=float, default=0.0)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    model_cost = MODEL_CATALOG[args.model]

    results = estimate_monthly_cost(
        prompt_tokens=args.prompt_tokens,
        completion_tokens=args.completion_tokens,
        rps=args.rps,
        active_hours_per_day=args.active_hours,
        active_days_per_month=args.active_days,
        model_cost=model_cost,
        cache_hit_rate=args.cache_hit_rate,
        cache_cost_per_request=args.cache_cost_per_request,
    )

    print("Model:", args.model)
    print("Description:", model_cost.description)
    print("Prompt tokens:", args.prompt_tokens)
    print("Completion tokens:", args.completion_tokens)
    print("Requests per second:", args.rps)
    print("Active hours/day:", args.active_hours)
    print("Active days/month:", args.active_days)
    print("Cache hit rate:", f"{args.cache_hit_rate:.0%}")
    print("")
    print("Cost per inference:", format_usd(results["cost_per_inference"]))
    print("Estimated monthly requests:", f"{results['requests_per_month']:,.0f}")
    print("Raw monthly cost:", format_usd(results["raw_monthly_cost"]))
    print("Cache monthly cost:", format_usd(results["cache_monthly_cost"]))
    print("Effective monthly cost:", format_usd(results["effective_monthly_cost"]))


if __name__ == "__main__":
    main()
