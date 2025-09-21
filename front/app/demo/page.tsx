"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Camera, Play, Pause, Volume2, Settings, BookOpen, Music, MessageSquare } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import Image from "next/image"

const LeadZeppelinLogo = ({ size = 24 }: { size?: number }) => (
  <Image
    src="/images/lead-zeppelin-logo.png"
    alt="Lead Zeppelin Logo"
    width={size}
    height={size}
    className={`h-${size / 4} w-${size / 4}`}
    style={{
      filter:
        "brightness(0) saturate(100%) invert(12%) sepia(89%) saturate(2851%) hue-rotate(346deg) brightness(95%) contrast(95%)",
    }}
  />
)

export default function DemoPage() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [selectedInstrument, setSelectedInstrument] = useState("piano")
  const [volume, setVolume] = useState([75])
  const [activeNotes, setActiveNotes] = useState<number[]>([])
  const [cameraPermission, setCameraPermission] = useState<"granted" | "denied" | "pending">("pending")
  const [cameraEnabled, setCameraEnabled] = useState(false)
  const [songUrl, setSongUrl] = useState("")
  const [currentLesson, setCurrentLesson] = useState("Mary Had A Little Lamb")
  const [nextNotes, setNextNotes] = useState(["C", "D", "E", "F"])
  const [aiFeedback, setAiFeedback] = useState("Great job! You're playing the notes correctly. Keep up the rhythm!")
  const videoRef = useRef<HTMLVideoElement>(null)
  const router = useRouter()

  const instruments = [
    { value: "piano", label: "Piano", icon: <LeadZeppelinLogo size={20} /> },
    { value: "guitar", label: "Guitar", icon: <LeadZeppelinLogo size={20} />, toBe: true },
    { value: "violin", label: "Violin", icon: <LeadZeppelinLogo size={20} />, toBe: true },
    { value: "drums", label: "Drums", icon: <LeadZeppelinLogo size={20} />, toBe: true },
    { value: "flute", label: "Flute", icon: <LeadZeppelinLogo size={20} />, toBe: true },
    { value: "saxophone", label: "Saxophone", icon: <LeadZeppelinLogo size={20} />, toBe: true },
  ]

  const lessons = [
    { name: "Mary Had A Little Lamb", difficulty: "Beginner", notes: 3, description: "Simple 3-note configuration perfect for beginners" },
    { name: "Twinkle Twinkle Little Star", difficulty: "Beginner", notes: 5, description: "Classic nursery rhyme with 5-note range" },
    { name: "Happy Birthday", difficulty: "Beginner", notes: 6, description: "Celebrate with this 6-note birthday song" },
    { name: "Full Chromatic Scale", difficulty: "Advanced", notes: 12, description: "Complete 12-note setup for advanced playing" },
    { name: "Ode to Joy", difficulty: "Intermediate", notes: 8, description: "Beethoven's famous melody with 8-note range" },
    { name: "Canon in D", difficulty: "Advanced", notes: 10, description: "Pachelbel's beautiful canon arrangement" },
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

  const selectLesson = (lessonName: string) => {
    setCurrentLesson(lessonName)
    // Update next notes based on lesson
    if (lessonName === "Mary Had A Little Lamb") {
      setNextNotes(["E", "D", "C", "D"])
    } else if (lessonName === "Twinkle Twinkle Little Star") {
      setNextNotes(["C", "C", "G", "G"])
    } else {
      setNextNotes(["C", "D", "E", "F"])
    }
  }

  const handleSongUrlSubmit = () => {
    // This would integrate with the backend to parse notes
    console.log("Parsing song from URL:", songUrl)
    setAiFeedback("Analyzing sheet music... Please wait while we process the notes.")
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 max-w-screen-2xl items-center">
          <Link href="/" className="flex items-center space-x-2">
            <LeadZeppelinLogo size={32} />
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
            <Link href="/demo" className="text-sm font-medium hover:text-primary transition-colors">
              Live Demo
            </Link>
          </nav>
        </div>
      </header>

      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">🎵 Live Demo - Three Column Layout 🎵</h1>
          <p className="text-muted-foreground">
            Experience real-time paper-to-MIDI conversion with visual feedback and multiple instrument sounds.
          </p>
          <div className="mt-4 p-4 bg-red-100 border border-red-300 rounded-lg">
            <p className="text-red-800 font-bold text-lg">🚨 THREE COLUMN LAYOUT - LEFT | MIDDLE | RIGHT 🚨</p>
          </div>
        </div>

        {/* THREE COLUMN LAYOUT */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* LEFT COLUMN - Controls (3/12 columns) */}
          <div className="lg:col-span-3 space-y-6">
            <div className="p-4 bg-blue-100 border border-blue-300 rounded-lg">
              <p className="text-blue-800 font-bold">LEFT COLUMN - CONTROLS</p>
            </div>
            
            {/* Instrument Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LeadZeppelinLogo size={20} />
                  Instrument
                </CardTitle>
                <CardDescription>Choose your virtual instrument</CardDescription>
              </CardHeader>
              <CardContent>
                <Select value={selectedInstrument} onValueChange={setSelectedInstrument}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select instrument" />
                  </SelectTrigger>
                  <SelectContent>
                    {instruments.map((instrument) => (
                      <SelectItem key={instrument.value} value={instrument.value}>
                        <span className="flex items-center gap-2">
                          {instrument.icon}
                          {instrument.label}
                          {instrument.toBe && <span className="text-blue-400 text-xs ml-1">*To Be Added*</span>}
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* Playback and Volume Controls */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
                  Playback & Audio
                </CardTitle>
                <CardDescription>Start or stop the live demo and control volume</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
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

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Volume</span>
                    <span className="text-sm text-muted-foreground">{volume[0]}%</span>
                  </div>
                  <Slider value={volume} onValueChange={setVolume} max={100} min={0} step={1} className="w-full" />
                </div>

                {cameraPermission === "denied" && (
                  <p className="text-sm text-destructive">
                    Camera access denied. Please enable camera permissions.
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Camera Settings */}
            <Card className="h-[350px]">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Camera className="h-5 w-5" />
                  Camera Settings
                </CardTitle>
                <CardDescription>Configure camera detection settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4 flex flex-col justify-between h-full">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="camera-toggle">Enable Camera</Label>
                    <Switch id="camera-toggle" checked={cameraEnabled} onCheckedChange={setCameraEnabled} />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="sensitivity">Detection Sensitivity</Label>
                    <Badge variant="outline">Medium</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="resolution">Camera Resolution</Label>
                    <Badge variant="outline">1080p</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="framerate">Frame Rate</Label>
                    <Badge variant="outline">30 FPS</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="quality">Video Quality</Label>
                    <Badge variant="outline">High</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="stabilization">Image Stabilization</Label>
                    <Badge variant="outline">On</Badge>
                  </div>
                </div>
                <div className="space-y-3">
                  <Button className="w-full" variant="outline">
                    <Settings className="h-4 w-4 mr-2" />
                    Customize your layout! <span className="text-red-500 font-bold ml-1">**ADVANCED**</span>
                  </Button>
                  <div className="text-xs text-muted-foreground text-center">
                    More camera settings available in advanced mode
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* MIDDLE COLUMN - Lessons (3/12 columns) */}
          <div className="lg:col-span-3 space-y-6">
            <div className="p-4 bg-green-100 border border-green-300 rounded-lg">
              <p className="text-green-800 font-bold">MIDDLE COLUMN - LESSONS</p>
            </div>
            
            {/* Lead Zeppelin Lessons */}
            <Card className="h-[400px]">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  Lead Zeppelin Lessons
                </CardTitle>
                <CardDescription>Select a preset configuration to get started quickly</CardDescription>
              </CardHeader>
              <CardContent className="overflow-y-auto">
                <div className="space-y-3">
                  {lessons.map((lesson) => (
                    <Button
                      key={lesson.name}
                      variant="outline"
                      className="h-auto p-4 text-left justify-start bg-transparent w-full"
                      onClick={() => selectLesson(lesson.name)}
                    >
                      <div>
                        <div className="font-semibold text-sm mb-1">{lesson.name}</div>
                        <div className="text-xs text-muted-foreground mb-2">{lesson.description}</div>
                        <div className="flex gap-2">
                          <Badge variant="secondary" className="text-xs">
                            {lesson.difficulty}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {lesson.notes} notes
                          </Badge>
                        </div>
                      </div>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Retrieve Sheet Music */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Music className="h-5 w-5" />
                  Retrieve Sheet Music
                </CardTitle>
                <CardDescription>Parse notes from any song URL</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  type="url"
                  placeholder="https://noobnotes.net/..."
                  value={songUrl}
                  onChange={(e) => setSongUrl(e.target.value)}
                  className="w-full"
                />
                <Button 
                  className="w-full" 
                  disabled={!songUrl.trim()}
                  onClick={handleSongUrlSubmit}
                >
                  <Music className="h-4 w-4 mr-2" />
                  Parse Notes
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* RIGHT COLUMN - Camera Feed and Feedback (6/12 columns) */}
          <div className="lg:col-span-6 space-y-6">
            <div className="p-4 bg-purple-100 border border-purple-300 rounded-lg">
              <p className="text-purple-800 font-bold">RIGHT COLUMN - CAMERA FEED & FEEDBACK</p>
            </div>
            
            {/* Live Camera Feed */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Camera className="h-5 w-5" />
                    Live Camera Feed
                  </span>
                  {isPlaying && cameraPermission === "granted" && (
                    <Badge variant="default" className="flex items-center gap-1">
                      <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
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
                      <p className="text-lg font-semibold text-blue-800">{currentLesson}</p>
                    </div>
                    <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                      Beginner
                    </Badge>
                  </div>
                </div>

                <div className="mb-4">
                  <Button 
                    className="w-full" 
                    variant={isPlaying ? "destructive" : "default"}
                    onClick={togglePlaying}
                  >
                    {isPlaying ? (
                      <>
                        <Pause className="h-4 w-4 mr-2" />
                        Stop lesson
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Start lesson
                      </>
                    )}
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
                          {cameraPermission === "denied" ? "Camera access denied" : 'Click "Start lesson" to begin'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Next Notes and AI Feedback */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Next Notes */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Music className="h-5 w-5" />
                    Next Notes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="text-center p-3 bg-primary/10 rounded-lg">
                      <p className="text-sm text-muted-foreground">Next Note:</p>
                      <p className="text-2xl font-bold text-primary">{nextNotes[0]}</p>
                    </div>
                    <div className="flex gap-2 justify-center">
                      {nextNotes.slice(1, 4).map((note, i) => (
                        <Badge key={i} variant="outline" className="text-sm">
                          {note}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* AI Teacher Feedback */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="h-5 w-5" />
                    AI Teacher Feedback
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-sm">{aiFeedback}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}