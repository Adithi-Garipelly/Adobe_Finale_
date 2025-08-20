#!/usr/bin/env python3
"""
Test script to verify delete endpoint
"""
import requests

def test_delete_endpoint():
    """Test the delete endpoint"""
    base_url = "http://localhost:8080"
    
    # First, list files to see what's available
    try:
        response = requests.get(f"{base_url}/files")
        print(f"Files endpoint response: {response.status_code}")
        if response.status_code == 200:
            files = response.json().get('files', [])
            print(f"Available files: {files}")
            
            if files:
                # Try to delete the first file
                test_file = files[0]
                print(f"\nTesting delete for: {test_file}")
                
                delete_response = requests.delete(f"{base_url}/delete/{test_file}")
                print(f"Delete response status: {delete_response.status_code}")
                print(f"Delete response: {delete_response.text}")
                
                # Check if file was actually deleted
                files_after = requests.get(f"{base_url}/files").json().get('files', [])
                print(f"Files after delete: {files_after}")
                
            else:
                print("No files available to test delete")
        else:
            print(f"Failed to get files: {response.text}")
            
    except Exception as e:
        print(f"Error testing delete: {e}")

if __name__ == "__main__":
    test_delete_endpoint()
