# ADO Instructions MCP Server

A modular## 🖼️ **Image Analysis**: Process workflow diagrams with dependency arrows using Azure OpenAI ✅ **NEW**MCP (Model Context Protocol) server that converts meeting transcripts, text inputs, and images into structured Azure DevOps work items using Azure OpenAI for advanced image analysis.

## 🆕 **New: Azure OpenAI Image Processing**

The server now includes advanced image analysis capabilities powered by Azure OpenAI's vision models:

- **🖼️ Advanced Image Analysis** - Uses Azure OpenAI o4-mini model for intelligent image understanding
- **📊 Workflow Diagram Recognition** - Identifies project structures and dependency arrows from visual diagrams
- **� Dependency Arrow Analysis** - Parses arrows to determine Epic → Task parent-child relationships  
- **🏗️ Hierarchical Structure Detection** - Creates proper work item hierarchy from visual flows

*Designed for analyzing wireframes, workflow diagrams with dependency arrows, and project documentation images.*

## 📝 **Text Analysis and Processing**

The server specializes in analyzing text content for requirements and work item generation:

- **📋 Requirements Extraction** - Identifies tasks and features from text content
- **🔗 Dependency Analysis** - Understands relationships between work items
- **📝 Smart Processing** - Extracts structured information from unstructured text
- **⚡ Fast Text Analysis** - Optimized for meeting notes and requirements documents

*Designed for processing meeting transcripts, requirements documents, and project text.*

## 🛠️ Available Tools

| Tool | Input | Output | Description |
|------|-------|--------|-------------|
| **process_meeting_transcript** | `transcript: str` | ADO instructions JSON | Process long meeting notes/transcripts |
| **process_feature_image** 🆕 | `image_base64: str`<br>`description: str` | ADO instructions JSON | **AZURE OPENAI**: Analyze workflow diagrams and dependency arrows using AI vision |
| **generate_ado_workitems_from_text** | `text_input: str`<br>`project_name: str`<br>`priority_override: str` | ADO instructions JSON | Flexible text-to-ADO conversion |
| **format_ado_instructions_summary** ⭐ | `instructions_json: str` | Formatted summary | Format work items for user review |
| **search_files_for_processing** 🔍 | `search_pattern: str`<br>`file_types: str`<br>`search_locations: str` | File search results | Find text and image files on PC |
| **validate_ado_structure** | `instructions_json: str` | Validation report | Validate JSON structure |
| **get_organization_context** | None | Organization details | Get Omar Solutions context |
| **load_image_from_file** 🆕 | `image_path: str` | Base64 image data | Load and convert images for processing |

## ✨ Features

- 📝 **Text Processing**: Convert meeting transcripts and notes into structured ADO work items ✅ **WORKING**
- 🖼️ **Image Analysis**: Process wireframes and diagrams using Azure OpenAI ✅ **NEW**
- 🔗 **Structured Output**: Generate properly hierarchized Epic → Task relationships ✅ **WORKING**
- 🎯 **Smart Prioritization**: Auto-assign priorities based on content analysis ✅ **WORKING**
- 📋 **Comprehensive Validation**: Ensure work item structure correctness ✅ **WORKING**
- ⭐ **User Confirmation**: Format summaries for review before proceeding ✅ **NEW**
- 🔍 **File Discovery**: Find text and image files on PC automatically ✅ **NEW**

## 🚀 Quick Start

### 1. Setup Dependencies
```bash
# Clone or navigate to project directory
cd ado_instructions

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies (already configured in pyproject.toml)
uv sync
```

### 2. Configure Azure OpenAI
Create or update `.env` file with your Azure OpenAI credentials:
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://omaragent.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=o4-mini-imagebot
AZURE_OPENAI_MODEL=o4-mini
```

### 3. Run the Server
```bash
# Start MCP server on default port 2000
python server.py

# Different port
python server.py --port 8001

# Different transport
python server.py --transport stdio
```

### 4. Connect from VS Code
Add to your MCP settings:
```json
{
  "mcpServers": {
    "ado-instructions": {
      "command": "python",
      "args": ["c:/path/to/your/ado_instructions/server.py"],
      "cwd": "c:/path/to/your/ado_instructions"
    }
  }
}
```

## 📖 Usage Examples

### 1. Basic Text Processing Workflow
```python
# Step 1: Process meeting transcript
result = process_meeting_transcript(
    transcript="Team discussed new user authentication system. Need login page, password reset, user registration, and admin dashboard. High priority for login and registration. Medium priority for password reset. Low priority for admin dashboard."
)

# Step 2: Format summary for user review
summary = format_ado_instructions_summary(result)
print(summary)

# Step 3: Present to user and ask for confirmation
# User reviews the formatted output and confirms/requests changes

# Step 4: Proceed with validated work items
validated_json = result  # If user approved
```

### 2. 🆕 Azure OpenAI Image Processing Workflow
```python
# Step 1: Load image from file
image_data = load_image_from_file(
    image_path="c:/path/to/wireframe.png"
)

# Step 2: Process image with Azure OpenAI
result = process_feature_image(
    image_base64=image_data,
    description="Wireframe showing user authentication flow with login, registration, and dashboard components"
)

# Step 3: Format summary for user review
summary = format_ado_instructions_summary(result)
print(summary)

# Step 4: Present to user and ask for confirmation
# User reviews the formatted output and confirms/requests changes

# Step 5: Proceed with validated work items
validated_json = result  # If user approved
```

### 3. Flexible Text Input Workflow
```python
# Step 1: Convert any text to ADO work items
result = generate_ado_workitems_from_text(
    text_input="Build a mobile app with user profiles, messaging, and notifications",
    project_name="Mobile App Development",
    priority_override="High"
)

# Step 2: Format summary for user review
summary = format_ado_instructions_summary(result)
print(summary)

# Step 3: Present to user and ask for confirmation
# User reviews the formatted output and confirms/requests changes

# Step 4: Proceed with validated work items
validated_json = result  # If user approved
```

## 🔗 Dependency Arrow Analysis for Workflow Diagrams

The **process_feature_image** tool includes advanced visual analysis to understand workflow dependencies from arrows and connections in diagrams:

### 📊 **Visual Pattern Recognition**
- **Arrow Direction Analysis**: `Parent → Child` relationships are identified from arrow flow
- **Hierarchical Structure Detection**: Creates proper Epic → Task relationships based on visual hierarchy
- **Dependency Chain Mapping**: Follows arrow sequences to understand process flows

### 🎯 **Supported Workflow Patterns**
| Visual Pattern | Interpretation | ADO Structure |
|----------------|----------------|---------------|
| `Database → Website → Frontend` | Sequential dependencies | **Epic**: Database Implementation<br>**Tasks**: Website, Frontend |
| `Login ← Dashboard ← Reports` | Reverse dependency flow | **Epic**: Dashboard<br>**Tasks**: Login, Reports |
| `API ↕ Database` | Bidirectional dependency | **Epic**: System Integration<br>**Tasks**: API, Database |

### 📝 **Example: Workflow Diagram Processing**
```
Input Image: [Database] → [Website] → [Frontend/Backend]

Expected Output:
- Epic: "Database Implementation" (parent)
  - Task: "Build Website" (child of Database)
  - Task: "Develop Frontend" (child of Website)  
  - Task: "Develop Backend" (child of Website)
```

### ⚠️ **Important**: 
When processing workflow diagrams, the system should:
1. **Identify the root Epic** from the leftmost/topmost element
2. **Follow arrows** to determine task dependencies
3. **Create hierarchical structure** where arrows indicate parent → child relationships
4. **Avoid creating multiple separate Epics** unless the diagram shows parallel workflows

### 4. File Discovery and Processing Workflow (🔍 NEW)
```python
# Step 1: Search for files on the PC
search_results = search_files_for_processing(
    search_pattern="wireframe",
    file_types="images,text",
    search_locations="desktop,documents"
)

# Step 2: Process found files
# User selects files from search results
# Load content and process with appropriate tool
```

## 🏗️ Project Structure

```
ado_instructions/
├── server.py                 # Main MCP server (FastMCP 2.11.2)
├── pyproject.toml           # Dependencies and project config
├── uv.lock                  # Dependency lock file
├── README.md                # This documentation
├── .env                     # Environment variables (Azure OpenAI config)
├── modules/
│   ├── __init__.py          # Module initialization
│   ├── models.py            # Data classes and enums
│   ├── config.py            # Environment and organization setup
│   ├── text_processor.py    # Text analysis and feature extraction
│   ├── image_processor.py   # 🆕 Azure OpenAI image analysis
│   ├── ado_generator.py     # ADO work item generation
│   ├── file_search.py       # File discovery functionality
│   ├── error_handling.py    # Comprehensive error management
│   └── common_utils.py      # Shared utilities
└── tests/
    ├── test_optimization.py # Performance tests
    ├── test_utils.py        # Utility tests
    ├── images/              # Test image files
    └── text/                # Test text files
```

## 📊 Dependencies

### Core Dependencies (5 packages total)
- ✅ **fastmcp**: MCP framework (2.11.2)
- ✅ **uvicorn**: ASGI server
- ✅ **fastapi**: Web framework
- ✅ **python-dotenv**: Environment management
- ✅ **openai**: Azure OpenAI SDK for image processing 🆕

### Module Status
- ✅ Error handling (fallback processing)
- ✅ Common utilities (shared functions)
- ✅ Models (data classes and enums)
- ✅ Configuration (environment setup)
- ✅ Text processing (feature extraction)
- ✅ 🆕 Image processing (Azure OpenAI integration)
- ✅ ADO generation (work item creation)

## 📊 MCP Tools Reference

| Tool | Input | Output | Description |
|------|-------|--------|-------------|
| **process_meeting_transcript** | `transcript: str` | ADO instructions JSON | Process long meeting notes/transcripts |
| **process_feature_image** 🆕 | `image_base64: str`<br>`description: str` | ADO instructions JSON | Analyze images using Azure OpenAI vision |
| **generate_ado_workitems_from_text** | `text_input: str`<br>`project_name: str`<br>`priority_override: str` | ADO instructions JSON | Flexible text-to-ADO conversion |
| **format_ado_instructions_summary** ⭐ | `instructions_json: str` | Formatted summary | **NEW**: Format work items for user review |
| **validate_ado_structure** | `instructions_json: str` | Validation report | Validate JSON structure |
| **get_organization_context** | None | Organization details | Get Omar Solutions context |
| **search_files_for_processing** | `search_pattern: str`<br>`file_types: str`<br>`search_locations: str` | File search results | Find text and image files on PC |
| **load_image_from_file** 🆕 | `image_path: str` | Base64 image data | Load and convert images for processing |

### Tool-Specific Details

#### `process_meeting_transcript`
- **Purpose**: Convert meeting notes/transcripts to ADO work items
- **Input**: Long text containing meeting discussion
- **Output**: Structured JSON with Epics and Tasks
- **Use Case**: Transform unstructured meeting notes into organized work items

#### 🆕 `process_feature_image` (NEW - Azure OpenAI)
- **Purpose**: Analyze images using Azure OpenAI's advanced vision capabilities
- **Input**: Base64 image data + optional description
- **Output**: Structured JSON with Epics and Tasks
- **Use Case**: Extract requirements from wireframes, diagrams, and visual project documentation
- **Technology**: Azure OpenAI o4-mini model with vision capabilities

#### `generate_ado_workitems_from_text`
- **Purpose**: Flexible text-to-ADO conversion
- **Input**: Any text description + optional project name and priority
- **Output**: Structured JSON with Epics and Tasks
- **Use Case**: Quick conversion of requirements text to work items

#### ⭐ `format_ado_instructions_summary` (NEW)
- **Purpose**: Format work items for user review and confirmation
- **Input**: ADO instructions JSON from any generation tool
- **Output**: User-friendly formatted summary with project structure
- **Use Case**: Present work items to user for approval before proceeding

#### 🔍 `search_files_for_processing` (NEW)
- **Purpose**: Find text and image files on PC for processing
- **Input**: Search pattern, file types, locations
- **Output**: List of found files with paths and metadata
- **Use Case**: Discover relevant files without knowing exact paths

#### 🆕 `load_image_from_file` (NEW)
- **Purpose**: Load and convert local images to base64 format
- **Input**: Absolute path to image file
- **Output**: Base64 encoded image data
- **Use Case**: Prepare local images for Azure OpenAI processing

## 🔧 Module Details

### 📊 `modules/models.py`
- **WorkItem**: Data class for individual work items
- **ADOInstructions**: Container for complete project structure
- **WorkItemType**: Enum (Epic, Task, User Story, Bug)
- **Priority**: Enum (Low, Medium, High, Critical)
- **ORGANIZATION_CONTEXT**: Omar Solutions configuration

### ⚙️ `modules/config.py`
- **setup_environment()**: Load .env variables including Azure OpenAI config
- **get_organization_context()**: Access organization data
- **get_azure_openai_config()**: 🆕 Azure OpenAI configuration management

### 📝 `modules/text_processor.py`
- **extract_features_from_text()**: Extract project features from text
- **extract_requirements_from_text()**: Find specific requirements
- **determine_priority_from_text()**: Auto-assign priorities

### 🖼️ `modules/image_processor.py` 🆕 NEW
- **process_image_with_azure_openai()**: Analyze images using Azure OpenAI
- **extract_features_from_image()**: Extract project features from images
- **analyze_workflow_diagram()**: Specialized diagram analysis
- **format_image_analysis_result()**: Format AI analysis into ADO structure

### 🏗️ `modules/ado_generator.py`
- **create_epic_from_feature()**: Generate Epic work items
- **create_task_from_requirement()**: Generate Task work items
- **generate_ado_instructions()**: Complete instruction generation
- **format_ado_summary()**: Format work items for user review

### 🔍 `modules/file_search.py` ⭐ NEW
- **search_files_for_processing()**: Find text and image files on PC
- **format_search_results_for_display()**: User-friendly result formatting
- **get_search_usage_examples()**: Usage documentation and examples

## 🛠️ Advanced Configuration

### Azure OpenAI Setup
```bash
# .env file configuration
AZURE_OPENAI_ENDPOINT=https://omaragent.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=o4-mini-imagebot
AZURE_OPENAI_MODEL=o4-mini
```

### Server Options
```bash
# Custom port
python server.py --port 8001

# Different transport
python server.py --transport stdio
```

### Azure OpenAI Configuration Example
```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint="https://omaragent.openai.azure.com/",
    api_key=subscription_key
)

# Example image analysis call
response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are an expert at analyzing project diagrams and wireframes to extract requirements.",
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyze this wireframe and extract the project requirements"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        }
    ],
    max_completion_tokens=40000,
    model="o4-mini-imagebot"
)
```

## 🧪 Testing Dependency Arrow Analysis

### ✅ **Test Case 1: Linear Workflow**
```
Input Diagram: [Database] → [Website] → [Frontend]
Expected Output:
- Epic: "Database Implementation" 
- Task: "Build Website" (depends on Database)
- Task: "Develop Frontend" (depends on Website)
```

### ✅ **Test Case 2: Parallel Dependencies** 
```
Input Diagram: [API] → [Frontend]
                    ↘ [Backend]
Expected Output:
- Epic: "API Implementation"
- Task: "Develop Frontend" (depends on API)
- Task: "Develop Backend" (depends on API)
```

### ✅ **Test Case 3: Complex Workflow**
```
Input Diagram: [Database] → [API Layer] → [Authentication] → [User Interface]
Expected Output:
- Epic: "Database Implementation"
- Task: "Build API Layer" (depends on Database)
- Task: "Implement Authentication" (depends on API)
- Task: "Create User Interface" (depends on Authentication)
```

### 🔍 **Testing Your Workflow Diagrams**

1. **Create test images** with clear arrows showing dependencies
2. **Use descriptive context**: Include description explaining the workflow
3. **Verify hierarchy**: Check that ONE Epic is created with proper Task dependencies
4. **Review dependency chains**: Ensure Tasks reference their dependencies

```python
# Test workflow diagram processing
result = process_feature_image(
    image_base64=your_workflow_diagram,
    description="Website development workflow: Database → Website → Frontend/Backend dependencies"
)

# Should generate:
# - 1 Main Epic (not multiple Epics)
# - Tasks with dependency context
# - Proper workflow sequence preserved
```

### ❌ **Common Issues to Avoid**
- **Multiple Epics**: Should create ONE Epic from workflow root
- **Missing Dependencies**: Tasks should reference what they depend on
- **Wrong Hierarchy**: Follow arrows for parent → child relationships
- **Lost Sequence**: Preserve workflow order shown by arrows
)
```

### Dependency Management
The server gracefully handles missing dependencies:
- **Azure OpenAI**: Falls back to text-only processing if API key unavailable
- **Image Processing**: Uses fallback methods if Azure OpenAI is unavailable
- **All modules**: Comprehensive error handling with fallbacks

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| **ModuleNotFoundError** | Activate virtual environment: `.venv\Scripts\Activate.ps1` |
| **Azure OpenAI API errors** | Check API key and endpoint configuration in .env |
| **Image processing failures** | Verify Azure OpenAI deployment and model availability |
| **Port already in use** | Change port: `python server.py --port 8001` |
| **Import errors** | Check module structure and relative imports |
| **Text processing errors** | Verify input format and content |

## 🎯 Best Practices

### ⭐ NEW: File Discovery Workflow
- ✅ **Use search tool first**: Find files without knowing exact paths
- ✅ **Filter by type**: Search for "images", "text", or "all" file types
- ✅ **Multiple locations**: Search desktop, documents, downloads simultaneously  
- ✅ **Pattern matching**: Use wildcards or keywords to find specific files
- ✅ **Check file sizes**: Avoid processing very large files

### ⭐ NEW: User Confirmation Workflow
- ✅ **Always format and present** work items after generation
- ✅ **Ask user confirmation**: "Are these instructions correct?"
- ✅ **Offer modifications** if user wants changes
- ✅ **Document any changes** requested by the user
- ✅ **Validate final output** before proceeding

### For Text Inputs:
- ✅ Use action-oriented language ("build", "create", "implement")
- ✅ Mention specific technologies or features
- ✅ Include requirements and acceptance criteria
- ✅ Test with various input lengths

### 🆕 For Image Inputs:
- ✅ Use clear wireframes or diagrams
- ✅ Provide descriptive context in the description field
- ✅ Supported formats: PNG, JPG, GIF, BMP, WebP
- ✅ Keep images under 10MB for optimal processing
- ✅ Ensure good contrast and readable text in diagrams
- ✅ Include workflow arrows and clear component relationships

### For Development:
- ✅ Follow modular architecture principles
- ✅ Add comprehensive error handling
- ✅ Include type hints and docstrings
- ✅ Test modules independently

## 🚀 Next Steps

1. **Enhanced Azure OpenAI Integration**: Improve image analysis accuracy and speed
2. **Advanced Visual Analysis**: Better UI component detection in wireframes
3. **Multi-Modal Processing**: Combine text and image inputs for richer analysis
4. **ADO Integration**: Direct API integration for work item creation
5. **AI Enhancement**: LLM-powered requirement analysis
6. **Web Interface**: Optional web UI for easier testing

## 🏆 Successfully Tested Features

- ✅ **Text Processing**: Handles complex project descriptions
- ✅ **Modular Architecture**: All modules working independently (6 modules)
- ✅ **Server Startup**: Runs on configured port (2000) with 8 tools  
- ✅ **Error Handling**: Graceful fallbacks for missing dependencies
- ✅ **MCP Integration**: Compatible with VS Code MCP framework
- ✅ **ADO Generation**: Produces valid work item structures
- ✅ ⭐ **NEW**: **Formatted Summaries**: User-friendly work item presentation
- ✅ ⭐ **NEW**: **User Confirmation Workflow**: Ask before proceeding
- ✅ ⭐ **NEW**: **Priority Display**: Clear "High/Medium/Low" labels
- ✅ 🔍 **NEW**: **File Search**: Find images and text files on PC automatically
- ✅ 🏗️ **NEW**: **Clean Server Architecture**: Modularized file search functionality
- ✅ 🆕 **NEW**: **Azure OpenAI Integration**: Advanced image analysis with o4-mini

## 📋 Current Tool Count: **8 MCP Tools Available**

1. `process_meeting_transcript` - Convert meeting notes to ADO work items
2. 🆕 `process_feature_image` - **NEW**: Analyze images using Azure OpenAI
3. `generate_ado_workitems_from_text` - Flexible text-to-ADO conversion
4. ⭐ `format_ado_instructions_summary` - **NEW**: Format work items for user review
5. 🔍 `search_files_for_processing` - **NEW**: Find images/text files on PC
6. `validate_ado_structure` - Verify JSON structure correctness
7. `get_organization_context` - Get Omar Solutions context information
8. 🆕 `load_image_from_file` - **NEW**: Load and convert images for processing

---

**Ready for advanced image processing with Azure OpenAI!** 🎉 🖼️ ✨
