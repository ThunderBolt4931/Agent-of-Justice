# Agent-of-Justice

# Courtroom Simulation System

This project simulates a courtroom trial using AI agents to represent different courtroom roles (judge, lawyers, witnesses, etc.). The system processes legal cases through a structured trial process and outputs verdict predictions.

## Features

- **Multi-agent simulation**: AI agents with distinct roles and behaviors
- **Structured trial process**: 
  - Phase 1: Opening statements
  - Phase 2: Witness examination
  - Phase 3: Closing arguments
  - Phase 4: Verdict delivery
- **Dynamic witness creation**: Ability to generate witness agents on-the-fly
- **Transcript logging**: Complete record of all courtroom proceedings
- **Batch processing**: Can handle multiple cases from CSV input

## System Components

### Core Classes

1. **CourtAgent**: Base class for all courtroom participants
   - Handles conversation history and responses
   - Uses Groq API for LLM interactions
   - Configurable system prompts for different roles

2. **CourtSimulation**: Main controller for trial proceedings
   - Manages all agents and trial phases
   - Maintains trial transcript
   - Coordinates interactions between agents

### Agent Roles

- Judge
- Defense Lawyer
- Prosecution
- Defendant
- Plaintiff
- Witnesses (dynamically created)

## Usage

### Single Case Simulation

```python
test_case = """
The plaintiff alleges that the defendant, a former employee, violated a non-compete agreement...
"""

simulation = CourtSimulation("test_1", test_case)
verdict = simulation.run_full_trial()
print(f"Final verdict: {'GRANTED' if verdict == 1 else 'DENIED'}")
```

### Batch Processing

```python
submission = process_case_file("input_cases.csv")
submission.to_csv("predictions.csv", index=False)
```

## System Prompts

Each agent role has a detailed system prompt defining:
- Their goals and responsibilities
- Communication style
- Ethical boundaries
- Role-specific behaviors

## Requirements

- Python 3.7+
- Required packages:
  - `groq`
  - `pandas`
  
## Configuration

Set your Groq API key in the `CourtAgent` class initialization.

## Output

The system produces:
- Real-time console output of trial proceedings
- Complete transcript of all statements
- Final verdict (1 for GRANTED, 0 for DENIED)
- CSV output for batch processing

## Example Case

The repository includes sample case data in CSV format for testing batch processing functionality.

## Limitations

- Currently uses a fixed LLM model (llama3-70b-8192)
- Simplified legal reasoning compared to real court proceedings
- Basic witness examination process

## Future Enhancements

- Add objection handling
- Incorporate more sophisticated evidence presentation
- Support for jury trials
- Configurable trial procedures
