#!/usr/bin/env python3
"""
Simple SSE client for testing the Django SSE implementation.

This script helps verify that:
1. SSE endpoints are working correctly
2. Authentication is properly handled
3. Events are being sent and received
4. Connection management is working

Usage:
    python test_sse_client.py
    python test_sse_client.py --test-auth --email user@example.com --password password123
"""

import asyncio
import aiohttp
import json
import argparse
import sys
from urllib.parse import urlencode


class SSETestClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None

    async def login(self, email, password):
        """Login and get access token"""
        login_url = f"{self.base_url}/api/v1/auth/login/"
        login_data = {"email": email, "password": password}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(login_url, json=login_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data.get("access")
                        print(
                            f"✅ Login successful! Token: {self.access_token[:20]}..."
                        )
                        return True
                    else:
                        error_data = await response.text()
                        print(f"❌ Login failed ({response.status}): {error_data}")
                        return False
            except Exception as e:
                print(f"❌ Login error: {e}")
                return False

    async def test_simple_sse(self):
        """Test the simple SSE endpoint without authentication"""
        print("\n🧪 Testing simple SSE endpoint (no auth)...")

        test_url = f"{self.base_url}/api/v1/auth/sse/test/"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url) as response:
                    if response.status != 200:
                        print(
                            f"❌ Failed to connect to SSE test endpoint: {response.status}"
                        )
                        return False

                    print(f"✅ Connected to SSE test endpoint")
                    print(f"📡 Content-Type: {response.headers.get('Content-Type')}")
                    print(f"📡 Cache-Control: {response.headers.get('Cache-Control')}")

                    message_count = 0
                    async for line in response.content:
                        line = line.decode("utf-8").strip()
                        if line.startswith("data:"):
                            message_count += 1
                            print(f"📨 Message {message_count}: {line}")

                            # Stop after receiving 5 messages
                            if message_count >= 5:
                                print("✅ Received expected messages, stopping test")
                                break

                    return True

        except Exception as e:
            print(f"❌ SSE test error: {e}")
            return False

    async def test_authenticated_sse(self):
        """Test the authenticated SSE endpoint"""
        if not self.access_token:
            print("❌ No access token available. Please login first.")
            return False

        print("\n🔐 Testing authenticated SSE endpoint...")

        # Test with query parameter authentication
        params = {"token": self.access_token}
        sse_url = f"{self.base_url}/api/v1/auth/sse/notifications/?{urlencode(params)}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(sse_url) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(
                            f"❌ Failed to connect to authenticated SSE: {response.status}"
                        )
                        print(f"Error: {error_text}")
                        return False

                    print(f"✅ Connected to authenticated SSE endpoint")
                    print(f"📡 Content-Type: {response.headers.get('Content-Type')}")
                    print(f"📡 Connection: {response.headers.get('Connection')}")

                    print("⏳ Waiting for events (30 seconds)...")

                    message_count = 0
                    start_time = asyncio.get_event_loop().time()
                    timeout = 30  # seconds

                    async for line in response.content:
                        current_time = asyncio.get_event_loop().time()
                        if current_time - start_time > timeout:
                            print("⏰ Timeout reached, stopping test")
                            break

                        line = line.decode("utf-8").strip()
                        if line.startswith("event:") or line.startswith("data:"):
                            message_count += 1
                            print(f"📨 SSE Line {message_count}: {line}")

                            # Parse complete events
                            if line.startswith("data:"):
                                try:
                                    data_part = line[
                                        5:
                                    ].strip()  # Remove 'data:' prefix
                                    if data_part and data_part != "{}":
                                        event_data = json.loads(data_part)
                                        print(f"🎯 Parsed Event: {event_data}")
                                except json.JSONDecodeError:
                                    print(f"⚠️  Could not parse JSON: {data_part}")

                    print(f"✅ Received {message_count} SSE lines")
                    return True

        except Exception as e:
            print(f"❌ Authenticated SSE error: {e}")
            return False

    async def test_header_authentication(self):
        """Test SSE with Authorization header (may not work with standard EventSource)"""
        if not self.access_token:
            print("❌ No access token available. Please login first.")
            return False

        print("\n🔑 Testing SSE with Authorization header...")

        sse_url = f"{self.base_url}/api/v1/auth/sse/notifications/"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(sse_url, headers=headers) as response:
                    print(f"📊 Response Status: {response.status}")
                    print(f"📡 Content-Type: {response.headers.get('Content-Type')}")

                    if response.status == 200:
                        print("✅ Authorization header authentication works!")

                        # Read a few lines to confirm
                        line_count = 0
                        async for line in response.content:
                            line = line.decode("utf-8").strip()
                            if line:
                                print(f"📨 Line {line_count + 1}: {line}")
                                line_count += 1
                                if line_count >= 3:  # Just read a few lines
                                    break
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Header auth failed: {error_text}")
                        return False

        except Exception as e:
            print(f"❌ Header auth error: {e}")
            return False

    async def run_all_tests(self, email=None, password=None):
        """Run all SSE tests"""
        print("🚀 Starting SSE Test Suite")
        print(f"🌐 Base URL: {self.base_url}")

        results = {}

        # Test 1: Simple SSE (no auth)
        results["simple_sse"] = await self.test_simple_sse()

        # Test 2: Login (if credentials provided)
        if email and password:
            results["login"] = await self.login(email, password)

            if results["login"]:
                # Test 3: Authenticated SSE with query param
                results["auth_sse_query"] = await self.test_authenticated_sse()

                # Test 4: Authenticated SSE with header
                results["auth_sse_header"] = await self.test_header_authentication()
        else:
            print("\n⚠️  Skipping authentication tests (no credentials provided)")
            print(
                "   Use --test-auth --email <email> --password <password> to test auth"
            )

        # Summary
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)

        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:20} {status}")

        total_tests = len(results)
        passed_tests = sum(results.values())

        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
            return False


async def main():
    parser = argparse.ArgumentParser(description="Test SSE implementation")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the Django server",
    )
    parser.add_argument(
        "--test-auth", action="store_true", help="Test authenticated endpoints"
    )
    parser.add_argument("--email", help="Email for authentication test")
    parser.add_argument("--password", help="Password for authentication test")

    args = parser.parse_args()

    if args.test_auth and (not args.email or not args.password):
        print("❌ --test-auth requires --email and --password")
        sys.exit(1)

    client = SSETestClient(args.base_url)

    try:
        success = await client.run_all_tests(args.email, args.password)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if aiohttp is available
    try:
        import aiohttp
    except ImportError:
        print("❌ aiohttp is required for this test script")
        print("Install it with: pip install aiohttp")
        sys.exit(1)

    asyncio.run(main())
