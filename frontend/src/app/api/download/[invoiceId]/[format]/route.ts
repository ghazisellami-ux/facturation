import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ invoiceId: string; format: string }> }
) {
  const { invoiceId, format } = await params;
  const token = request.nextUrl.searchParams.get('token');

  if (!token) {
    return NextResponse.json({ error: 'Token requis' }, { status: 401 });
  }

  if (!['pdf', 'xml'].includes(format)) {
    return NextResponse.json({ error: 'Format invalide' }, { status: 400 });
  }

  // Server-side: use internal Docker URL; fallback to public URL
  const backendUrl = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
  const url = `${backendUrl}/api/invoices/${invoiceId}/${format}?token=${token}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      return NextResponse.json({ error: 'Erreur backend' }, { status: response.status });
    }

    const data = await response.arrayBuffer();
    const contentType = format === 'pdf' ? 'application/pdf' : 'application/xml';
    const disposition = format === 'pdf' ? 'inline' : 'attachment';
    const ext = format;

    return new NextResponse(data, {
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Content-Disposition': `${disposition}; filename="facture.${ext}"`,
      },
    });
  } catch {
    return NextResponse.json({ error: 'Erreur de connexion au serveur' }, { status: 502 });
  }
}
