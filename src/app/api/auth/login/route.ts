import { NextRequest, NextResponse } from "next/server";
import { getUserByEmail, updateUser } from "@/lib/auth/db";
import { verifyPassword, generateToken } from "@/lib/auth/utils";
import { LoginData } from "@/lib/auth/types";

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { email, password } = body as LoginData;

    // Validate input
    if (!email || !password) {
      return NextResponse.json(
        { error: "Email and password are required" },
        { status: 400 }
      );
    }

    // Find user by email
    const user = getUserByEmail(email);
    if (!user) {
      return NextResponse.json(
        { error: "Invalid email or password" },
        { status: 401 }
      );
    }

    // Verify password
    const isPasswordValid = verifyPassword(password, user.password);
    if (!isPasswordValid) {
      return NextResponse.json(
        { error: "Invalid email or password" },
        { status: 401 }
      );
    }

    // Update last login time
    updateUser(user.id, { lastLogin: new Date().toISOString() });

    // Generate JWT token
    const token = generateToken(user);

    // Return user data (excluding password) and token
    const { password: _, ...userWithoutPassword } = user;

    return NextResponse.json({
      user: userWithoutPassword,
      token,
    });
  } catch (error) {
    console.error("Error in login route:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}