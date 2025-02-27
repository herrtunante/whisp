import { NextRequest, NextResponse } from "next/server";
import { getUserById } from "@/lib/auth/db";
import { verifyToken } from "@/lib/auth/utils";

export async function GET(req: NextRequest) {
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
    
    // Verify token
    const decoded = verifyToken(token);
    if (!decoded) {
      return NextResponse.json(
        { error: "Invalid or expired token" },
        { status: 401 }
      );
    }
    
    // Get user data
    const user = getUserById(decoded.id);
    if (!user) {
      return NextResponse.json(
        { error: "User not found" },
        { status: 404 }
      );
    }
    
    // Return user data without password
    const { password, ...userWithoutPassword } = user;
    
    return NextResponse.json({ user: userWithoutPassword });
  } catch (error) {
    console.error("Error in user route:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}