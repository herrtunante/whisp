// components/Navbar.tsx
"use client"

import Link from 'next/link';
import Image from 'next/image';
import { useState } from 'react';
import { useAuth } from '@/lib/hooks/useAuth';

const Navbar: React.FC = () => {
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
    const { user, isLoggedIn, logoutUser } = useAuth();

    return (
        <nav className="bg-gray-800 text-white p-4 mb-4">
            <div className="w-full flex justify-between">
                <div className="flex md:mx-12 justify-center items-center h-full">
                    <Link href={isLoggedIn ? "/dashboard" : "/"} className="text-lg hover:text-gray-300 flex items-center">
                        <Image
                            src="/whisp_logo.svg"
                            alt="Whisp Logo"
                            width={35}
                            height={35}
                        />
                        <strong className="font-bold ml-2">WHISP</strong>
                    </Link>
                </div>

                <div className="flex mx-12 justify-end items-center">
                    <Link target="_blank" href="https://openforis.org/solutions/whisp" className="hover:text-gray-300 mx-4">
                        About
                    </Link>

                    <div className="relative mx-4">
                        <button 
                            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                            className="hover:text-gray-300"
                        >
                            Documentation
                        </button>
                        {isDropdownOpen && (
                            <div className="absolute top-full left-0 mt-2 w-48 bg-gray-700 shadow-lg rounded-lg z-10">
                                <Link 
                                    href="/documentation/layers" 
                                    className="block px-4 py-2 hover:bg-gray-600 rounded-t-lg"
                                    onClick={() => setIsDropdownOpen(false)}
                                >
                                    Layers
                                </Link>
                                <Link 
                                    href="/documentation/api-guide" 
                                    className="block px-4 py-2 hover:bg-gray-600"
                                    onClick={() => setIsDropdownOpen(false)}
                                >
                                    API Guide
                                </Link>
                                {isLoggedIn && (
                                    <Link 
                                        href="/api-token-guide" 
                                        className="block px-4 py-2 hover:bg-gray-600 rounded-b-lg"
                                        onClick={() => setIsDropdownOpen(false)}
                                    >
                                        API Token Guide
                                    </Link>
                                )}
                            </div>
                        )}
                    </div>

                    {isLoggedIn ? (
                        <div className="relative ml-4">
                            <button
                                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                                className="flex items-center hover:text-gray-300"
                            >
                                <span className="mr-2">{user?.name.split(' ')[0]}</span>
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                            </button>
                            {isUserMenuOpen && (
                                <div className="absolute top-full right-0 mt-2 w-48 bg-gray-700 shadow-lg rounded-lg z-10">
                                    <Link 
                                        href="/dashboard" 
                                        className="block px-4 py-2 hover:bg-gray-600 rounded-t-lg"
                                        onClick={() => setIsUserMenuOpen(false)}
                                    >
                                        Dashboard
                                    </Link>
                                    <Link 
                                        href="/api-token-guide" 
                                        className="block px-4 py-2 hover:bg-gray-600"
                                        onClick={() => setIsUserMenuOpen(false)}
                                    >
                                        API Token
                                    </Link>
                                    {/* Show admin link only for admin users */}
                                    {(user?.email === 'admin@example.com' || user?.email === 'sanchez.paus@gmail.com') && (
                                        <Link 
                                            href="/admin" 
                                            className="block px-4 py-2 hover:bg-gray-600"
                                            onClick={() => setIsUserMenuOpen(false)}
                                        >
                                            Admin Dashboard
                                        </Link>
                                    )}
                                    <button
                                        onClick={() => {
                                            logoutUser();
                                            setIsUserMenuOpen(false);
                                        }}
                                        className="block w-full text-left px-4 py-2 hover:bg-gray-600 rounded-b-lg"
                                    >
                                        Logout
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="flex ml-4">
                            <Link href="/login" className="hover:text-gray-300 mr-4">
                                Login
                            </Link>
                            <Link href="/register" className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded">
                                Register
                            </Link>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
