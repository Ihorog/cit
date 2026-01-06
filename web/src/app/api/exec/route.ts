import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.API_URL || 'http://127.0.0.1:8790';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, input } = body;

    if (!action) {
      return NextResponse.json(
        { error: 'Action is required' },
        { status: 400 }
      );
    }

    // Forward request to backend API
    const response = await fetch(`${API_URL}/api/exec`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ action, input: input || {} }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: `Backend API error: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Exec API error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: String(error) },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    endpoint: '/api/exec',
    method: 'POST',
    description: 'Execute actions on Ci orchestrator',
    actions: [
      'actions.registry.get',
      'actions.node_packages.get',
      'actions.state.get',
      'actions.state.set',
      'actions.event.emit',
      'actions.event.list'
    ]
  });
}
