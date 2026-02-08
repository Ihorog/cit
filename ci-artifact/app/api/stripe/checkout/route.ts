import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { getSupabase } from '@/lib/supabase';
import { getCiStatus } from '@/lib/ci-engine';
import type { CiContext, CiStatus } from '@/lib/ci-engine';
import { createHash } from 'crypto';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

const VALID_CONTEXTS: CiContext[] = ['career', 'love', 'timing'];
const VALID_STATUSES: CiStatus[] = ['PROCEED', 'HOLD', 'NOT_NOW'];

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { artifact_code, context, status, locked_minute_utc } = body;

    if (!artifact_code || !context || !status || locked_minute_utc == null) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    if (!VALID_CONTEXTS.includes(context)) {
      return NextResponse.json({ error: 'Invalid context' }, { status: 400 });
    }

    if (!VALID_STATUSES.includes(status)) {
      return NextResponse.json({ error: 'Invalid status' }, { status: 400 });
    }

    // Verify deterministic status matches
    const expectedStatus = getCiStatus(context, locked_minute_utc);
    if (expectedStatus !== status) {
      return NextResponse.json({ error: 'Status mismatch' }, { status: 400 });
    }

    const ip = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ?? 'unknown';
    const ipHash = createHash('sha256').update(ip).digest('hex').slice(0, 16);
    const verifyHash = createHash('sha256')
      .update(`${artifact_code}:${context}:${status}:${locked_minute_utc}`)
      .digest('hex');

    // Insert artifact record
    const { error: insertError } = await getSupabase()
      .from('artifacts')
      .insert({
        artifact_code,
        context,
        status,
        locked_minute_utc,
        verify_hash: verifyHash,
        ip_hash: ipHash,
      });

    if (insertError) {
      console.error('Supabase insert failed:', insertError.message);
      return NextResponse.json({ error: 'Failed to create artifact' }, { status: 500 });
    }

    const baseUrl = process.env.NEXT_PUBLIC_URL ?? 'http://localhost:3000';

    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: { name: `ci-Artifact · ${context}` },
            unit_amount: 500,
          },
          quantity: 1,
        },
      ],
      metadata: { artifact_code },
      success_url: `${baseUrl}/verify/${artifact_code}`,
      cancel_url: `${baseUrl}/artifact`,
    });

    return NextResponse.json({ url: session.url });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    console.error('Checkout error:', message);
    return NextResponse.json({ error: 'Checkout failed' }, { status: 500 });
  }
}
