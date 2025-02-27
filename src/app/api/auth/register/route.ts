import { NextRequest, NextResponse } from "next/server";
import { createUser } from "@/lib/auth/db";
import { hashPassword, generateToken } from "@/lib/auth/utils";
import { RegisterUserData } from "@/lib/auth/types";

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { email, password, name } = body as RegisterUserData;

    // Validate input
    if (!email || !password || !name) {
      return NextResponse.json(
        { error: "Email, password, and name are required" },
        { status: 400 }
      );
    }

    // Hash password
    const hashedPassword = hashPassword(password);

    // Create user
    try {
      const user = createUser({
        email,
        password: hashedPassword,
        name,
      });

      // Generate JWT token
      const token = generateToken(user);

      // Return user data (excluding password) and token
      const { password: _, ...userWithoutPassword } = user;

      return NextResponse.json({
        user: userWithoutPassword,
        token,
      });
    } catch (error: any) {
      return NextResponse.json(
        { error: error.message || "Failed to create user" },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error("Error in register route:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}