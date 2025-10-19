"""
Utility script to validate API configurations.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def check_api_key(name: str, env_var: str, required: bool = True) -> bool:
    """Check if an API key is configured."""
    value = os.getenv(env_var)
    
    if value and value != f"your_{env_var.lower()}":
        print(f"  ✓ {name}: Configured")
        return True
    else:
        if required:
            print(f"  ✗ {name}: Missing (Required)")
        else:
            print(f"  ⚠ {name}: Missing (Optional)")
        return not required


def check_configuration():
    """Check all API configurations."""
    print("=" * 60)
    print("API Configuration Check")
    print("=" * 60)
    
    print("\nRequired APIs:")
    required_ok = all([
        check_api_key("OpenAI", "OPENAI_API_KEY", required=True),
        check_api_key("Apollo", "APOLLO_API_KEY", required=True),
    ])
    
    print("\nOptional APIs:")
    check_api_key("Clay", "CLAY_API_KEY", required=False)
    check_api_key("Clearbit", "CLEARBIT_API_KEY", required=False)
    check_api_key("PeopleDataLabs", "PEOPLEDATALABS_API_KEY", required=False)
    check_api_key("SendGrid", "SENDGRID_API_KEY", required=False)
    
    print("\nEmail Configuration:")
    from_email = os.getenv("SENDGRID_FROM_EMAIL")
    if from_email and "@" in from_email:
        print(f"  ✓ SendGridFrom Email: {from_email}")
    else:
        print(f"  ✗ SendGrid From Email: Not configured")
    
    print("\nGoogle Sheets:")
    creds_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    
    if os.path.exists(creds_file):
        print(f"  ✓ Credentials file: {creds_file}")
    else:
        print(f"  ⚠ Credentials file: Not found (optional)")
    
    if sheet_id:
        print(f"  ✓ Sheet ID: Configured")
    else:
        print(f"  ⚠ Sheet ID: Not configured (optional)")
    
    print("\n" + "=" * 60)
    
    if required_ok:
        print("✓ Minimum required configuration is complete")
        print("\nYou can run the workflow with:")
        print("  python langgraph_builder.py")
    else:
        print("✗ Missing required configuration")
        print("\nPlease configure missing API keys in .env file")
        print("See .env.example for reference")
    
    print("=" * 60)
    
    return required_ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if check_configuration() else 1)
