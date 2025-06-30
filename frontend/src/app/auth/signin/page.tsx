"use client";

import { useAuth } from "@/lib/auth";
import { GoogleLogoIcon } from "@phosphor-icons/react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function SignIn() {
  const { user, login, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (user) {
      router.push("/");
    }
  }, [user, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-base-100">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-base-100">
      <div className="card w-96 bg-base-200 shadow-xl">
        <div className="card-body items-center text-center">
          <h2 className="card-title text-2xl mb-6">Sign in to AutoQA</h2>
          <p className="mb-6">Log in to access automated testing features</p>
          <button
            onClick={login}
            className="btn btn-primary w-full flex items-center justify-center gap-2"
          >
            <GoogleLogoIcon className="h-5 w-5" weight="fill" />
            Sign in with Google
          </button>
        </div>
      </div>
    </div>
  );
}
