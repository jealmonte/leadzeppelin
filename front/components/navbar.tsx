'use client'

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Github } from "lucide-react"
import Image from "next/image"
import { useRouter, usePathname } from 'next/navigation'

export default function Navbar() {
  const router = useRouter()
  const pathname = usePathname()

  const scrollToSection = (sectionId: string) => {
    // If on homepage, scroll directly
    if (pathname === '/') {
      const element = document.getElementById(sectionId)
      if (element) {
        element.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        })
      }
    } else {
      // If on different page, navigate to homepage then scroll
      router.push(`/#${sectionId}`)
    }
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 max-w-screen-xl items-center justify-between px-6">
        <div className="flex items-center space-x-8">
          <Link href="/" className="flex items-center space-x-3">
            <Image
              src="/images/lead-zeppelin-logo.png"
              alt="Lead Zeppelin Logo"
              width={48}
              height={48}
              className="h-12 w-12"
              style={{
                filter:
                  "brightness(0) saturate(100%) invert(12%) sepia(89%) saturate(2851%) hue-rotate(346deg) brightness(95%) contrast(95%)",
              }}
            />
            <span className="font-bold text-xl">Lead Zeppelin</span>
          </Link>
          <nav className="flex items-center space-x-8">
            <button 
              onClick={() => scrollToSection('about')}
              className="text-sm font-medium transition-colors hover:text-primary cursor-pointer"
            >
              About Us
            </button>
            <button 
              onClick={() => scrollToSection('features')}
              className="text-sm font-medium transition-colors hover:text-primary cursor-pointer"
            >
              Features
            </button>
            <Link href="/configure" className="text-sm font-medium transition-colors hover:text-primary">
              Configure
            </Link>
            <Link href="/demo" className="text-sm font-medium transition-colors hover:text-primary">
              Live Demo
            </Link>
          </nav>
        </div>

        <nav className="flex items-center space-x-6">
          <Link href="https://github.com/jealmonte/leadzeppelin" target="_blank" rel="noreferrer">
            <Button variant="ghost" size="icon">
              <Github className="h-4 w-4" />
              <span className="sr-only">GitHub</span>
            </Button>
          </Link>
          <Link href="/contact">
            <Button variant="ghost" size="sm">
              Contact
            </Button>
          </Link>
          <Link href="/demo">
            <Button size="sm">Try Live Demo</Button>
          </Link>
        </nav>
      </div>
    </header>
  )
}
