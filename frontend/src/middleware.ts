import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { nextUrl } = request;
  const token = request.cookies.get('auth_token')?.value || 
                request.headers.get('authorization')?.replace('Bearer ', '');

  const isLoggedIn = !!token;

  // Public paths that don't require authentication
  const isPublicPath = 
    nextUrl.pathname === "/auth/signin" || 
    nextUrl.pathname.startsWith("/auth/") ||
    nextUrl.pathname.startsWith("/api/auth");

  // Redirect unauthenticated users to login page
  if (!isLoggedIn && !isPublicPath) {
    return NextResponse.redirect(new URL("/auth/signin", nextUrl));
  }

  // Redirect authenticated users away from login page
  if (isLoggedIn && nextUrl.pathname === "/auth/signin") {
    return NextResponse.redirect(new URL("/", nextUrl));
  }

  return NextResponse.next();
}

// Config for Middleware
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - /api/auth/* (auth API routes)
     * - /_next/* (Next.js internals)
     * - /fonts/* (static assets)
     * - /public/* (public assets)
     * - /images/* (public images)
     * - /favicon.ico, /sitemap.xml (public files)
     */
    "/((?!api/auth|_next/static|_next/image|fonts|public|images|favicon.ico|sitemap.xml).*)",
  ],
};