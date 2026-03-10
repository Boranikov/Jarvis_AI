from MCP.tool_registry import register_all_tools
from Skills.skills_manager import perform_skill, get_tool_schemas

def main():
    register_all_tools()
    print("Fetching tool schemas...")
    schemas = get_tool_schemas()
    print(f"Total tools discovered context: {len(schemas)}")
    
    print("\nAttempting to call MCP tool 'cloud_list' via perform_skill fallback...")
    try:
        result = perform_skill("cloud_list", {"path": "/"})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
