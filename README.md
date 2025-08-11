# ADO Instructions MCP Server

An MCP (Model Context Protocol) server that converts meeting transcripts and images into structured Azure DevOps work item instructions.

## Features

- 📝 **Text Processing**: Convert meeting transcripts and notes into structured ADO work items ✅ **WORKING**
- 🖼️ **Image Processing**: Analyze wireframes, diagrams, and sketches to extract requirements
- 🏗️ **Structured Output**: Generate properly hierarchized Epic → Task relationships ✅ **WORKING**
- ✅ **Validation**: Validate generated ADO instruction structures ✅ **WORKING**
- 🏢 **Organization Context**: Tailored for Omar Solutions (Data Engineering, Visualization, Analytics) ✅ **WORKING**

## Architecture

This project uses a **functional design pattern** for clean, maintainable code:
- No classes - pure functions organized in logical sections
- Clear separation of concerns
- Easy to test and debug
- FastMCP framework integration

## Quick Start

### 1. Install Dependencies
```bash
# Activate virtual environment (if already created)
.venv\Scripts\Activate.ps1

# Install required packages (already included in pyproject.toml)
pip install fastmcp
```

### 2. Run the MCP Server
```bash
python ado_instruction_server.py --transport http --port 8001
```

The server will start on `http://localhost:8001` with 5 available tools:
- `process_meeting_transcript` - Convert meeting notes to ADO work items
- `process_feature_image` - Analyze images for requirements
- `generate_ado_workitems_from_text` - Generate ADO structure from any text
- `validate_ado_structure` - Validate generated work items
- `get_organization_context` - Get Omar Solutions context info

### 3. Test with Real Data

#### Text Processing (✅ WORKING)
Use the sample requirements in `tests/text/Requirement.txt` which contains real SQL database requirements that successfully generate structured ADO work items.

#### Image Processing
Place images in `tests/images/` folder. Supported formats: JPG, JPEG, PNG, GIF, BMP, WebP

1. **Add images** (wireframes, diagrams) to `test_data/images/`
2. **Convert to base64** using the helper function:
```python
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Use with MCP tools
base64_data = image_to_base64("test_data/images/wireframe.png")
result = process_feature_image(base64_data, "Dashboard wireframe description")
```

## MCP Tools Available

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `process_meeting_transcript` | Process meeting notes | Long text | ADO instructions JSON |
| `process_feature_image` | Process visual requirements | Base64 image + description | ADO instructions JSON |
| `generate_ado_workitems_from_text` | Flexible text processing | Text + overrides | ADO instructions JSON |
| `validate_ado_structure` | Validate instruction format | JSON string | Validation report |
| `get_organization_context` | Get Omar Solutions context | None | Organization details |

## Example Workflow

### 1. Meeting Notes → ADO Work Items
```python
transcript = """
Product meeting: We need a customer analytics dashboard with real-time 
data visualization, user authentication, and mobile responsiveness.
Must integrate with CRM and support data export.
"""

result = process_meeting_transcript(transcript)
# Result: JSON with Epics and Tasks ready for ADO
```

### 2. Wireframe → ADO Work Items
```python
# Convert your wireframe image
base64_image = image_to_base64("wireframe.png")

result = process_feature_image(
    base64_image, 
    "Dashboard wireframe showing charts and user interface"
)
# Result: JSON with UI-focused Epics and Tasks
```

## Project Structure

```
ado_instructions/
├── ado_instruction_server.py    # Main MCP server
├── test_ado_server.py          # Direct testing script
├── test_mcp_client.py          # MCP client simulation
├── test_data/
│   ├── transcripts/            # Sample meeting notes
│   └── images/                 # Sample wireframes/diagrams
├── test_results/               # Generated test outputs
└── README.md                   # This file
```

## Sample Output Structure

```json
{
  "project_name": "Omar Solutions Analytics Dashboard Implementation",
  "feature_summary": "Implements 4 main features: Dashboard, Analytics, Authentication, Integration",
  "epics": [
    {
      "title": "Implement Dashboard Functionality",
      "description": "Develop and deploy Dashboard capability for Omar Solutions platform",
      "work_item_type": "Epic",
      "priority": 2,
      "tasks": [
        {
          "title": "Design Dashboard architecture",
          "work_item_type": "Task",
          "estimated_effort": "4-8 hours"
        }
      ],
      "acceptance_criteria": [
        "Dashboard functionality is implemented according to specifications",
        "Dashboard passes all unit and integration tests"
      ],
      "business_value": "Enhances Omar Solutions platform capabilities"
    }
  ]
}
```

## Best Practices for Testing

### For Text Inputs:
- ✅ Use realistic meeting transcripts
- ✅ Include action items and requirements
- ✅ Mention specific technologies or features
- ✅ Test with different text lengths (short notes vs. long transcripts)

### For Image Inputs:
- ✅ Use wireframes, mockups, or system diagrams
- ✅ Include descriptive text about the image
- ✅ Test with different image formats (PNG, JPG)
- ✅ Keep images under 5MB for better processing

### Validation Tips:
- ✅ Always validate generated JSON before using
- ✅ Check that Epics have associated Tasks
- ✅ Verify priority levels make sense
- ✅ Ensure business value statements are relevant

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Import errors | Ensure virtual environment is activated |
| No test data | Run test scripts to generate sample data |
| JSON validation fails | Check output format with `validate_ado_structure` |
| Image processing errors | Verify base64 encoding and file format |

## Next Steps

1. **Add real meeting transcripts** to test with your actual data
2. **Include wireframe images** for visual requirement processing  
3. **Customize organization context** for your specific needs
4. **Integrate with ADO APIs** for automatic work item creation
5. **Add AI/ML models** for enhanced text and image analysis

Happy testing! 🚀
