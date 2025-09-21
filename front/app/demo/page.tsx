"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Slider } from "@/components/ui/slider"
import { Camera, Play, Pause, Volume2, Settings, Zap, Circle } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

export default function DemoPage() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [selectedInstrument, setSelectedInstrument] = useState("piano")
  const [volume, setVolume] = useState([75])
  const [activeNotes, setActiveNotes] = useState<number[]>([])
  const [cameraPermission, setCameraPermission] = useState<"granted" | "denied" | "pending">("pending")
  const videoRef = useRef<HTMLVideoElement>(null)
  const router = useRouter()

  const instruments = [
    { value: "piano", label: "Piano", icon: "🎹" },
    { value: "guitar", label: "Guitar", icon: "🎸", toBe: true },
    { value: "violin", label: "Violin", icon: "🎻", toBe: true },
    { value: "drums", label: "Drums", icon: "🥁", toBe: true },
    { value: "flute", label: "Flute", icon: "🪈", toBe: true },
    { value: "saxophone", label: "Saxophone", icon: "🎷", toBe: true },
  ]

  const notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

  // Simulate camera access
  useEffect(() => {
    const requestCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true })
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }
        setCameraPermission("granted")
      } catch (error) {
        setCameraPermission("denied")
      }
    }

    if (isPlaying) {
      requestCamera()
    }
  }, [isPlaying])

  // Simulate note detection
  useEffect(() => {
    if (!isPlaying) return

    const interval = setInterval(() => {
      // Simulate random note detection
      const randomNotes = Array.from({ length: Math.floor(Math.random() * 3) + 1 }, () =>
        Math.floor(Math.random() * 12),
      )
      setActiveNotes(randomNotes)

      // Clear notes after a short duration
      setTimeout(() => setActiveNotes([]), 500)
    }, 1500)

    return () => clearInterval(interval)
  }, [isPlaying])

  const togglePlaying = () => {
    setIsPlaying(!isPlaying)
    if (!isPlaying) {
      setActiveNotes([])
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 max-w-screen-2xl items-center">
          <Link href="/" className="flex items-center space-x-2">
            <img
              src="/images/lead-zeppelin-logo.png"
              alt="Lead Zeppelin"
              className="h-8 w-8"
              style={{
                filter:
                  "brightness(0) saturate(100%) invert(18%) sepia(95%) saturate(3028%) hue-rotate(346deg) brightness(90%) contrast(95%)",
              }}
            />
            <span className="font-bold text-xl">Lead Zeppelin</span>
          </Link>
          <nav className="ml-auto flex items-center space-x-6">
            <Link href="/" className="text-sm font-medium hover:text-primary transition-colors">
              Home
            </Link>
            <Link href="#about" className="text-sm font-medium transition-colors hover:text-primary">
              About Us
            </Link>
            <Link href="#features" className="text-sm font-medium transition-colors hover:text-primary">
              Features
            </Link>
            <Link href="/configure" className="text-sm font-medium hover:text-primary transition-colors">
              Configure
            </Link>
          </nav>
        </div>
      </header>

      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Live Demo</h1>
          <p className="text-muted-foreground">
            Experience real-time paper-to-MIDI conversion with visual feedback and multiple instrument sounds.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Control Panel */}
          <div className="lg:col-span-1 space-y-6">
            {/* Playback Controls */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
                  Playback
                </CardTitle>
                <CardDescription>Start or stop the live demo</CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={togglePlaying} className="w-full" variant={isPlaying ? "destructive" : "default"}>
                  {isPlaying ? (
                    <>
                      <Pause className="h-4 w-4 mr-2" />
                      Stop Demo
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Start Demo
                    </>
                  )}
                </Button>

                {cameraPermission === "denied" && (
                  <p className="text-sm text-destructive mt-2">
                    Camera access denied. Please enable camera permissions.
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Instrument Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <img
                    src="/images/lead-zeppelin-logo.png"
                    alt="Lead Zeppelin"
                    className="h-5 w-5"
                    style={{
                      filter:
                        "brightness(0) saturate(100%) invert(18%) sepia(95%) saturate(3028%) hue-rotate(346deg) brightness(90%) contrast(95%)",
                    }}
                  />
                  Currently Playing
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-2xl mb-2">{instruments.find((i) => i.value === selectedInstrument)?.icon}</div>
                  <p className="font-medium text-lg">
                    {instruments.find((i) => i.value === selectedInstrument)?.label}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Volume Control */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Volume2 className="h-5 w-5" />
                  Audio
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Volume</span>
                    <span className="text-sm text-muted-foreground">{volume[0]}%</span>
                  </div>
                  <Slider value={volume} onValueChange={setVolume} max={100} min={0} step={1} className="w-full" />
                </div>
              </CardContent>
            </Card>

            {/* Performance Stats */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Performance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Notes Played:</span>
                  <Badge variant="secondary">47</Badge>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Accuracy:</span>
                  <Badge variant="default">94%</Badge>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Session Time:</span>
                  <Badge variant="outline">2:34</Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Demo Area */}
          <div className="lg:col-span-3 space-y-6">
            {/* Camera Feed */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Camera className="h-5 w-5" />
                    Live Camera Feed
                  </span>
                  {isPlaying && cameraPermission === "granted" && (
                    <Badge variant="default" className="flex items-center gap-1">
                      <Circle className="h-2 w-2 fill-current animate-pulse" />
                      Recording
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-blue-900">Current Lesson</p>
                      <p className="text-lg font-semibold text-blue-800">Mary Had A Little Lamb</p>
                    </div>
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                      Beginner
                    </Badge>
                  </div>
                </div>

                <div className="mb-4 space-y-2">
                  <Link href="/lesson">
                    <Button className="w-full bg-transparent" variant="outline">
                      <Play className="h-4 w-4 mr-2" />
                      Start lesson
                    </Button>
                  </Link>
                  <Button className="w-full" variant="secondary" onClick={() => router.push("/configure")}>
                    <Settings className="h-4 w-4 mr-2" />
                    Change lesson
                  </Button>
                </div>

                <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
                  {isPlaying && cameraPermission === "granted" ? (
                    <>
                      <video
                        ref={videoRef}
                        autoPlay
                        muted
                        className="absolute bottom-4 right-4 w-48 h-36 object-cover rounded border-2 border-white/50 z-10"
                      />

                      {/* Paper zone overlays */}
                      <div className="absolute inset-0 grid grid-cols-4 grid-rows-3 gap-1 p-4">
                        {Array.from({ length: 12 }, (_, i) => (
                          <div
                            key={i}
                            className={`
                              border-2 border-dashed rounded transition-all duration-200
                              ${activeNotes.includes(i) ? "border-primary bg-primary/20 shadow-lg" : "border-white/50"}
                            `}
                          >
                            {activeNotes.includes(i) && (
                              <div className="absolute inset-0 flex items-center justify-center">
                                <Badge variant="default" className="text-xs">
                                  {notes[i]}
                                </Badge>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </>
                  ) : (
                    <div className="flex items-center justify-center h-full text-white/70">
                      <div className="text-center">
                        <Camera className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p className="text-lg mb-2">Camera Feed</p>
                        <p className="text-sm">
                          {cameraPermission === "denied" ? "Camera access denied" : 'Click "Start Demo" to begin'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Active Notes Display */}
            <Card>
              <CardHeader>
                <CardTitle>Active Notes</CardTitle>
                <CardDescription>Real-time visualization of detected notes and musical feedback</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-12 gap-2 mb-4">
                  {notes.map((note, i) => (
                    <div
                      key={note}
                      className={`
                        h-16 rounded border-2 transition-all duration-200 flex items-center justify-center font-medium
                        ${
                          activeNotes.includes(i)
                            ? "border-primary bg-primary text-primary-foreground shadow-lg scale-105"
                            : "border-border bg-card text-card-foreground"
                        }
                      `}
                    >
                      {note}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
