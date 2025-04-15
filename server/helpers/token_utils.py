# server/helpers/token_utils.py

def calculate_token_cost(prompt_tokens, completion_tokens, cached_prompt_tokens=0,
                         model="o3-mini-2025-01-31"):
    """
    Calculate the cost of tokens for a given model using its pricing per 1 million tokens.
    
    Arguments:
      prompt_tokens (int): The number of new (non-cached) input tokens.
      cached_prompt_tokens (int, optional): The number of cached input tokens. Defaults to 0.
      completion_tokens (int): The number of output tokens.
      model (str, optional): The model identifier to use for pricing. 
                             Defaults to "o3-mini-2025-01-31".
    
    Returns:
      dict: A summary containing token counts and the respective cost breakdown:
          - prompt_tokens: tokens charged at the "input" rate.
          - cached_prompt_tokens: tokens charged at the "cached" rate (if applicable).
          - completion_tokens: tokens charged at the "output" rate.
          - total_tokens: sum of all tokens.
          - prompt_cost: cost for non-cached tokens.
          - cached_cost: cost for cached tokens.
          - completion_cost: cost for output tokens.
          - total_cost: overall cost.
    
    Raises:
      ValueError: if the provided model is not supported.
    """
    
    # Define pricing rates per 1 million tokens for each model.
    pricing = {
        "gpt-4.5-preview-2025-02-27": {"input": 75.00, "cached": 37.50, "output": 150.00},
        "gpt-4o-2024-08-06": {"input": 2.50, "cached": 1.25, "output": 10.00},
        "gpt-4o-2024-11-20": {"input": 2.50, "cached": 1.25, "output": 10.00},
        "gpt-4o-2024-05-13": {"input": 5.00, "cached": None, "output": 15.00},
        "gpt-4o-audio-preview-2024-12-17": {"input": 2.50, "cached": None, "output": 10.00},
        "gpt-4o-audio-preview-2024-10-01": {"input": 2.50, "cached": None, "output": 10.00},
        "gpt-4o-realtime-preview-2024-12-17": {"input": 5.00, "cached": 2.50, "output": 20.00},
        "gpt-4o-realtime-preview-2024-10-01": {"input": 5.00, "cached": 2.50, "output": 20.00},
        "gpt-4o-mini-2024-07-18": {"input": 0.15, "cached": 0.075, "output": 0.60},
        "gpt-4o-mini-audio-preview-2024-12-17": {"input": 0.15, "cached": None, "output": 0.60},
        "gpt-4o-mini-realtime-preview-2024-12-17": {"input": 0.60, "cached": 0.30, "output": 2.40},
        "o1-2024-12-17": {"input": 15.00, "cached": 7.50, "output": 60.00},
        "o1-preview-2024-09-12": {"input": 15.00, "cached": 7.50, "output": 60.00},
        "o1-pro-2025-03-19": {"input": 150.00, "cached": None, "output": 600.00},
        "o3-mini-2025-01-31": {"input": 1.10, "cached": 0.55, "output": 4.40},
        "o1-mini-2024-09-12": {"input": 1.10, "cached": 0.55, "output": 4.40},
        "gpt-4o-mini-search-preview-2025-03-11": {"input": 0.15, "cached": None, "output": 0.60},
        "gpt-4o-search-preview-2025-03-11": {"input": 2.50, "cached": None, "output": 10.00},
        "computer-use-preview-2025-03-11": {"input": 3.00, "cached": None, "output": 12.00}
    }
    
    rates = pricing.get(model)
    if rates is None:
        raise ValueError(f"The pricing for model '{model}' is not available.")
    
    # Calculate cost per 1 million tokens.
    prompt_cost = (prompt_tokens / 1_000_000) * rates["input"]
    
    if rates["cached"] is not None and cached_prompt_tokens:
        cached_cost = (cached_prompt_tokens / 1_000_000) * rates["cached"]
    else:
        cached_cost = 0
    
    completion_cost = (completion_tokens / 1_000_000) * rates["output"]
    
    total_cost = prompt_cost + cached_cost + completion_cost
    total_tokens = prompt_tokens + cached_prompt_tokens + completion_tokens
    
    return {
        "prompt_tokens": prompt_tokens,
        "cached_prompt_tokens": cached_prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "prompt_cost": prompt_cost,
        "cached_cost": cached_cost,
        "completion_cost": completion_cost,
        "total_cost": total_cost
    } 