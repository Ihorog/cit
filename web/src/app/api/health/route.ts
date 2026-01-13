import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.API_URL || 'http://127.0.0.1:8790';

export async function GET(request: NextRequest) {
  try {
    // Check backend API health
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      return NextResponse.json(
        { 
          status: 'error',
          backend: 'down',
          frontend: 'ok',
          timestamp: new Date().toISOString()
        },
        { status: 503 }
      );
    }

    const backendData = await response.json();
    
    return NextResponse.json({
      status: 'ok',
      backend: 'ok',
      frontend: 'ok',
      backendData,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Health check error:', error);
    return NextResponse.json(
      { 
        status: 'error',
        backend: 'unreachable',
        frontend: 'ok',
        error: String(error),
        timestamp: new Date().toISOString()
      },
      { status: 503 }
    );
  }
}
