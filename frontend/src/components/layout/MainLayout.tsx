'use client';

import { ReactNode } from 'react';
import Navbar from './Navbar';

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-base-100">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8">
        {children}
      </main>
      <footer className="bg-base-200 text-base-content">
        <div className="container mx-auto p-10">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div>
              <span className="footer-title">AutoQA</span> 
              <p className="mt-2">Automated quality assurance testing for your websites. Generate test plans, execute tests, and get detailed reports.</p>
            </div> 
            <div>
              <span className="footer-title">Features</span> 
              <ul className="mt-2 space-y-2">
                <li><a className="link link-hover">Automated Testing</a></li>
                <li><a className="link link-hover">AI-Generated Test Plans</a></li>
                <li><a className="link link-hover">Real-time Results</a></li>
                <li><a className="link link-hover">Detailed Reports</a></li>
              </ul>
            </div> 
            <div>
              <span className="footer-title">Contact</span> 
              <ul className="mt-2 space-y-2">
                <li><a className="link link-hover">About us</a></li>
                <li><a className="link link-hover">Documentation</a></li>
                <li><a className="link link-hover">GitHub</a></li>
              </ul>
            </div>
            <div>
              <span className="footer-title">Legal</span> 
              <ul className="mt-2 space-y-2">
                <li><a className="link link-hover">Terms of use</a></li>
                <li><a className="link link-hover">Privacy policy</a></li>
                <li><a className="link link-hover">Cookie policy</a></li>
              </ul>
              <p className="mt-4">© {new Date().getFullYear()} - AutoQA Web</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
