# Travel Lotara - Opik Evaluation System

Comprehensive LLM-as-a-judge evaluation framework for the Travel Lotara AI agent system using Comet Opik.

## ✨ NEW: Automatic Inline Evaluation

**Every user request is now automatically evaluated and logged to Comet!** 🎯

When your agent processes a request:
1. Agent generates response
2. **Automatic evaluation** runs (Gemini-powered LLM-as-judge)
3. **Metrics logged to Comet trace** with scores

View real-time evaluation in your Comet dashboard:
```
travel_lotara_root_agent/
├── inspiration_agent
├── planning_formatter_agent
└── inline_evaluation ⭐ (evaluation scores appear here!)
    ├── hallucination: 0.95
    ├── relevance: 0.88  
    ├── safety: 1.00
    └── quality: 0.82
```

**Enable/Disable:**
```bash
# Enabled by default
$env:ENABLE_INLINE_EVALUATION="true"

# To disable
$env:ENABLE_INLINE_EVALUATION="false"
```

## 🎯 Quick Start

### 1. Setup (5 minutes)

```bash
# Install dependencies
pip install opik litellm google-generativeai

# Set API keys
$env:OPIK_API_KEY="your-opik-key"      # Get from https://www.comet.com/signup
$env:GOOGLE_API_KEY="your-gemini-key"  # Get from https://makersuite.google.com/app/apikey
```

### 2. Test Inline Evaluation (2 minutes)

```bash
# Run example showing automatic evaluation
python tests/example_inline_evaluation.py
```

### 3. Run Full Demo (5 minutes)

```bash
# Comprehensive demo of all metrics
python tests/demo_opik_evaluations.py
```

This demonstrates:
- ✅ Hallucination detection
- ✅ Answer relevance scoring
- ✅ RAG context quality (precision/recall)
- ✅ Safety/moderation checks
- ✅ Custom travel quality metrics

### 3. View Results

Go to https://www.comet.com/opik/projects to see your evaluation dashboard!

## 📁 File Structure

```
src/travel_lotara/core/eval/
├── opik_showcase.py           # 🌟 Main: Opik LLM-as-judge metrics (Gemini-powered)
├── inline_evaluation.py       # ⭐ NEW: Automatic evaluation for each request
├── opik_evaluators.py         # Custom Opik metric classes
├── judges.py                  # LLM judge framework
├── experiments.py             # A/B testing & experiments
└── online_evals/              # Online evaluation tools

tests/
├── example_inline_evaluation.py   # ⭐ NEW: Inline eval examples
├── demo_opik_evaluations.py       # 🎬 Full demo (START HERE!)
├── evaluate_live_agent.py         # 🔧 Evaluate real agent outputs
├── eval_test_dataset.py           # 📊 Test cases & examples

docs/
└── OPIK_EVALUATION_GUIDE.md       # 📖 Complete guide
```

## 🚀 Usage Examples

### Example 1: Automatic Inline Evaluation (Recommended!)

```bash
# Just use your agent normally - evaluation happens automatically!
python tests/example_inline_evaluation.py
```

Your agent code automatically evaluates each response:
```python
# No changes needed! Evaluation is automatic via callbacks
agent = get_root_agent()
result = agent.run("Plan a trip to Paris")

# Evaluation runs automatically and logs to Comet trace
# Check Comet UI to see the scores!
```

### Example 2: Manual Evaluation

```bash
# Evaluate specific agent output
python tests/evaluate_live_agent.py --query "Plan a 5-day trip to Tokyo"
```

### Example 3: Full Demo

```bash
# Run all demonstrations
python tests/demo_opik_evaluations.py
```

### Example 3: Custom Evaluation

```python
from src.travel_lotara.core.eval.opik_showcase import (
    OpikMetricsShowcase,
    create_evaluation_sample
)

# Create evaluator
showcase = OpikMetricsShowcase(model="openai/gpt-4o-mini")

# Create sample
sample = create_evaluation_sample(
    sample_id="test_001",
    user_query="What's the best time to visit Bali?",
    agent_output="The bes (Gemini-Powered)

1. **Hallucination** - Detects false claims  
   `Hallucination(model="gemini/gemini-2.0-flash-exp")`  ⭐ Default

2. **Answer Relevance** - Checks if answer matches query  
   `AnswerRelevance(model="gemini/gemini-2.0-flash-exp")`

3. **Context Precision** - Evaluates RAG context quality  
   `ContextPrecision(model="gemini/gemini-2.0-flash-exp")`

4. **Context Recall** - Checks if all relevant info included  
   `ContextRecall(model="gemini/gemini-2.0-flash-exp")`

5. **Moderation** - Safety & policy compliance  
   `Moderation(model="gemini/gemini-2.0-flash-exp
2. **Answer Relevance** - Checks if answer matches query  
   `AnswerRelevance(model="openai/gpt-4o-mini")`

3. **Context Precision** - Evaluates RAG context quality  
   `ContextPrecision(model="openai/gpt-4o-mini")`

4. **Context Recall** - Checks if all relevant info included  
   `ContextRecall(model="openai/gpt-4o-mini")`

5. **Moderation** - Safety & policy compliance  
   `Moderation(model="openai/gpt-4o-mini")`

### Custom Metrics

6. **Travel Quality G-Eval** - Travel-specific quality assessment
7. **Agent Task Completion** - Did agent complete the task?
8. **Agent Tool Correctness** - Were right tools used?

## 🎓 Learn More

- **Full Guide**: [docs/OPIK_EVALUATION_GUIDE.md](docs/OPIK_EVALUATION_GUIDE.md)
- **Opik Docs**: https://www.comet.com/docs/opik/
- **Metrics Reference**: https://www.comet.com/docs/opik/evaluation/metrics/overview

## 🔑 Key Features

✅ **Automatic Inline Evaluation** - Every request evaluated in real-time ⭐ NEW!  
✅ **Gemini-Powered** - Fast, free LLM-as-judge (default model)  
✅ **Pre-built Metrics** - Use Opik's proven LLM-as-judge metrics  
✅ **Custom Metrics** - Travel-specific quality evaluations  
✅ **Auto-Logging** - All results logged to Opik dashboard  
✅ **Test Dataset** - Comprehensive test cases included  
✅ **Live Evaluation** - Evaluate real agent outputs  
✅ **A/B Testing** - Compare different prompts/models  
✅ **Regression Testing** - Prevent quality degradation  
✅ **Comet Integration** - Seamless tracing with your agent execution  

##NEW: See automatic inline evaluation
python tests/example_inline_evaluation.py

# Demo all metrics
python tests/demo_opik_evaluations.py

# Evaluate live query
python tests/evaluate_live_agent.py --query "YOUR_QUERY"

# Run test suite  
python tests/evaluate_live_agent.py --test-suite golden

# Use different judge model (Gemini is default)
python tests/evaluate_live_agent.py --query "Plan Paris trip" --model openai/gpt-4o-mini

# Use different judge model
python tests/evaluate_live_agent.py --query "Plan Paris trip" --model anthropic/claude-3-5-sonnet-20241022
```

## 🐛 Troubleshooting

**"NoGOOGLE_API_KEY="your-gemini-key"  # For Gemini (default)
```

**"Import error"**
```bash
pip install opik litellm google-generativeai
```

**"Inline evaluation not working"**
```bash
# Check if enabled
$env:ENABLE_INLINE_EVALUATION="true"

# Check logs
python -c "from src.travel_lotara.core.eval.inline_evaluation import get_inline_evaluator; print(get_inline_evaluator().enabled)"
**"Import error"**
```bash
pip install opik litellm openai anthropic
```

## 📈 Score Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 0.90-1.00 | Excellent ✅ | Deploy |
| 0.75-0.89 | Good ⚠️ | Minor fixes |
| 0.60-0.74 | Acceptable ⚠️ | Review |
| 0.00-0.59 | Poor ❌ | Major issues |

## 🤝 Support

- 💬 [Opik Discord](https://discord.gg/opik)
- 📧 support@comet.com
- 📚 [Full Documentation](docs/OPIK_EVALUATION_GUIDE.md)

---

**Built for the Encode Club x Comet Hackathon** 🏆

Demonstrating best-in-class LLM evaluation using Opik's powerful metrics framework.
