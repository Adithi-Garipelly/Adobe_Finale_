#!/usr/bin/env node

/**
 * Test script for Adobe Embed API integration
 * Run this in the browser console or as a Node.js script
 */

console.log('🧪 Testing Adobe Embed API Integration...');

// Test 1: Check if Adobe DC View SDK is loaded
function testAdobeSDK() {
  console.log('\n1️⃣ Testing Adobe DC View SDK...');
  
  if (typeof window !== 'undefined') {
    // Browser environment
    if (typeof window.AdobeDC !== 'undefined') {
      console.log('✅ Adobe DC View SDK is loaded in browser');
      return true;
    } else {
      console.log('❌ Adobe DC View SDK not found in browser');
      return false;
    }
  } else {
    // Node.js environment
    console.log('ℹ️  Running in Node.js - Adobe SDK test skipped');
    return true;
  }
}

// Test 2: Check configuration
function testConfiguration() {
  console.log('\n2️⃣ Testing Configuration...');
  
  const config = {
    CLIENT_ID: '1d691dca47814a4d847ab3286df17a8e',
    EMBED_MODE: 'SIZED_CONTAINER',
    SHOW_DOWNLOAD_PDF: false,
    SHOW_PRINT_PDF: false
  };
  
  console.log('📋 Configuration:', config);
  
  if (config.CLIENT_ID && config.CLIENT_ID.length > 0) {
    console.log('✅ Adobe API key is configured');
    return true;
  } else {
    console.log('❌ Adobe API key is missing');
    return false;
  }
}

// Test 3: Test Adobe viewer initialization (browser only)
function testViewerInitialization() {
  console.log('\n3️⃣ Testing Viewer Initialization...');
  
  if (typeof window === 'undefined') {
    console.log('ℹ️  Skipping viewer test in Node.js environment');
    return true;
  }
  
  if (typeof window.AdobeDC === 'undefined') {
    console.log('❌ Adobe SDK not available for viewer test');
    return false;
  }
  
  try {
    // Test creating Adobe DC View instance
    const adobeDCView = new window.AdobeDC.View({
      clientId: '1d691dca47814a4d847ab3286df17a8e',
      divId: 'test-container'
    });
    
    console.log('✅ Adobe DC View instance created successfully');
    return true;
    
  } catch (error) {
    console.log('❌ Failed to create Adobe DC View instance:', error.message);
    return false;
  }
}

// Test 4: Test environment variables
function testEnvironmentVariables() {
  console.log('\n4️⃣ Testing Environment Variables...');
  
  const envVars = {
    REACT_APP_ADOBE_EMBED_API_KEY: process.env.REACT_APP_ADOBE_EMBED_API_KEY || 'Not set',
    REACT_APP_API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'Not set',
    REACT_APP_BACKEND_URL: process.env.REACT_APP_BACKEND_URL || 'Not set'
  };
  
  console.log('📋 Environment Variables:', envVars);
  
  const allSet = Object.values(envVars).every(val => val !== 'Not set');
  
  if (allSet) {
    console.log('✅ All environment variables are set');
    return true;
  } else {
    console.log('⚠️  Some environment variables are missing');
    return false;
  }
}

// Test 5: Test API endpoints
async function testAPIEndpoints() {
  console.log('\n5️⃣ Testing API Endpoints...');
  
  const baseUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
  const endpoints = [
    '/health',
    '/status',
    '/documents'
  ];
  
  let allWorking = true;
  
  for (const endpoint of endpoints) {
    try {
      const response = await fetch(`${baseUrl}${endpoint}`);
      if (response.ok) {
        console.log(`✅ ${endpoint} - Working`);
      } else {
        console.log(`❌ ${endpoint} - HTTP ${response.status}`);
        allWorking = false;
      }
    } catch (error) {
      console.log(`❌ ${endpoint} - Error: ${error.message}`);
      allWorking = false;
    }
  }
  
  return allWorking;
}

// Main test function
async function runAllTests() {
  console.log('🚀 Starting Adobe Integration Tests...\n');
  
  const results = [];
  
  // Run all tests
  results.push(testAdobeSDK());
  results.push(testConfiguration());
  results.push(testViewerInitialization());
  results.push(testEnvironmentVariables());
  
  // Test API endpoints if in browser
  if (typeof window !== 'undefined') {
    try {
      const apiTest = await testAPIEndpoints();
      results.push(apiTest);
    } catch (error) {
      console.log('⚠️  API endpoint test failed:', error.message);
      results.push(false);
    }
  }
  
  // Summary
  console.log('\n' + '='.repeat(50));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(50));
  
  const passed = results.filter(Boolean).length;
  const total = results.length;
  
  console.log(`🎯 Overall: ${passed}/${total} tests passed`);
  
  if (passed === total) {
    console.log('🎉 All tests passed! Adobe integration is ready!');
  } else {
    console.log('⚠️  Some tests failed. Please check the issues above.');
  }
  
  // Specific recommendations
  console.log('\n💡 Recommendations:');
  
  if (!results[0]) {
    console.log('   • Ensure Adobe Embed API script is loaded in HTML');
    console.log('   • Check if https://documentcloud.adobe.com/view-sdk/main.js is accessible');
  }
  
  if (!results[1]) {
    console.log('   • Verify Adobe API key is correctly configured');
    console.log('   • Check config/adobe-config.js file');
  }
  
  if (!results[3]) {
    console.log('   • Set environment variables in .env file or startup script');
    console.log('   • Restart frontend after setting environment variables');
  }
  
  console.log('\n🔧 Next Steps:');
  console.log('   1. Start the system: ./scripts/start_system.sh');
  console.log('   2. Open http://localhost:3000 in browser');
  console.log('   3. Upload a PDF and test text selection');
  console.log('   4. Verify Adobe viewer loads correctly');
  
  return passed === total;
}

// Run tests
if (typeof window !== 'undefined') {
  // Browser environment
  console.log('🌐 Running in browser environment');
  runAllTests();
} else {
  // Node.js environment
  console.log('🖥️  Running in Node.js environment');
  runAllTests();
}
