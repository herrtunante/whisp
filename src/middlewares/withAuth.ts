import { NextRequest, NextResponse } from "next/server";

export const withAuth = (handler: Function) => {
  return async (req: NextRequest, ...args: any[]) => {
    // Skip auth for auth endpoints
    const { pathname } = new URL(req.url);
    if (pathname.startsWith("/api/auth/")) {
      return handler(req, ...args);
    }

    // Get token from Authorization header or query parameter
    const authHeader = req.headers.get("Authorization");
    const url = new URL(req.url);
    const apiTokenParam = url.searchParams.get("apiToken");
    
    let token = "";
    
    if (authHeader && authHeader.startsWith("Bearer ")) {
      token = authHeader.split(" ")[1];
    } else if (apiTokenParam) {
      token = apiTokenParam;
    }
    
    if (!token) {
      return NextResponse.json(
        { error: "API token is required. Please include it as a Bearer token in the Authorization header or as an apiToken query parameter." },
        { status: 401 }
      );
    }
    
    // In a real implementation, we would verify the token here
    // Since our db.ts now uses localStorage which isn't available in Edge
    // We'll simplify this for the demo version
    
    // Add user ID to the request for use in handlers
    const modifiedReq = new Request(req, {
      headers: new Headers(req.headers)
    });
    // Add a dummy user ID
    (modifiedReq.headers as any).set("X-User-ID", "demo-user-id");
    
    return handler(modifiedReq, ...args);
  };
};