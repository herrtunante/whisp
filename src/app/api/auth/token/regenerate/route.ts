import { NextRequest, NextResponse } from "next/server";
import { getUserById, regenerateApiToken } from "@/lib/auth/db";
import { verifyToken } from "@/lib/auth/utils";

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    // Get token from Authorization header
    const authHeader = req.headers.get("Authorization");
    
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json(
        { error: "Authorization token is required" },
        { status: 401 }
      );
    }
    
    const token = authHeader.split(" ")[1];
    
    // Verify token - in a real app this would validate against JWT
    // For demo purposes, we're using a simplified approach
    const decoded = verifyToken(token);
    if (!decoded) {
      return NextResponse.json(
        { error: "Invalid or expired token" },
        { status: 401 }
      );
    }
    
    // Get user data - using a dummy ID for demo purposes
    // In a real app, the ID would come from the JWT token
    const userId = decoded.id || 'demo-user';
    const user = getUserById(userId);
    
    if (!user) {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
      );
    }
    
    // Regenerate API token
    const newApiToken = regenerateApiToken(user.id);
    
    return NextResponse.json({ apiToken: newApiToken });
  } catch (error) {
    console.error("Error regenerating API token:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}