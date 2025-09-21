"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Camera, Play, Pause, ArrowLeft, CheckCircle, Circle } from "lucide-react"
import Link from "next/link"

export default function LessonPage() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const [cameraPermission, setCameraPermission] = useState<"granted" | "denied" | "pending">("pending")
  const [activeNotes, setActiveNotes] = useState<number[]>([])
  const videoRef = useRef<HTMLVideoElement>(null)

  const lessonSteps = [
    { note: "E", instruction: "Place your finger on the top-left zone and press E", completed: false },
    { note: "D", instruction: "Move to the second zone and press D", completed: false },
    { note: "C", instruction: "Move to the third zone and press C", completed: false },
    { note: "D", instruction: "Back to the second zone for D", completed: false },
    { note: "E", instruction: "Return to E", completed: false },
    { note: "E", instruction: "E again", completed: false },
    { note: "E", instruction: "Hold E", completed: false },
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

  // Simulate lesson progress
  useEffect(() => {
    if (!isPlaying) return

    const interval = setInterval(() => {
      // Simulate note detection for lesson
      const expectedNote = lessonSteps[currentStep]?.note
      if (expectedNote) {
        const noteIndex = notes.indexOf(expectedNote)
        setActiveNotes([noteIndex])

        // Auto-advance lesson for demo
        setTimeout(() => {
          setActiveNotes([])
          if (currentStep < lessonSteps.length - 1) {
            setCurrentStep((prev) => prev + 1)
            setProgress(((currentStep + 1) / lessonSteps.length) * 100)
          }
        }, 1000)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [isPlaying, currentStep])

  const togglePlaying = () => {
    setIsPlaying(!isPlaying)
    if (!isPlaying) {
      setActiveNotes([])
      setCurrentStep(0)
      setProgress(0)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center">
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
            <Link
              href="/demo"
              className="flex items-center gap-2 text-sm font-medium hover:text-primary transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Demo
            </Link>
          </nav>
        </div>
      </header>

      <div className="container mx-auto py-8 px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Learn How To Play Mary Had A Little Lamb</h1>
          <p className="text-muted-foreground">
            Follow along with the guided lesson to learn this classic song step by step.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Lesson Progress */}
          <div className="lg:col-span-1 space-y-6">
            {/* Progress Card */}
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
                  Lesson Progress
                </CardTitle>
                <CardDescription>Track your learning progress</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Progress</span>
                      <span>{Math.round(progress)}%</span>
                    </div>
                    <Progress value={progress} className="w-full" />
                  </div>

                  <div className="text-center">
                    <Badge variant="outline" className="text-lg px-4 py-2">
                      Step {currentStep + 1} of {lessonSteps.length}
                    </Badge>
                  </div>

                  <Button onClick={togglePlaying} className="w-full" variant={isPlaying ? "destructive" : "default"}>
                    {isPlaying ? (
                      <>
                        <Pause className="h-4 w-4 mr-2" />
                        Pause Lesson
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Start Lesson
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Current Step */}
            <Card>
              <CardHeader>
                <CardTitle>Current Step</CardTitle>
              </CardHeader>
              <CardContent>
                {lessonSteps[currentStep] && (
                  <div className="space-y-3">
                    <div className="text-center">
                      <Badge variant="default" className="text-2xl px-6 py-3">
                        {lessonSteps[currentStep].note}
                      </Badge>
                    </div>
                    <p className="text-sm text-center text-muted-foreground">{lessonSteps[currentStep].instruction}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Main Lesson Area */}
          <div className="lg:col-span-3 space-y-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2 mb-4">
                <img
                  src="/images/lead-zeppelin-logo.png"
                  alt="Lead Zeppelin"
                  className="h-6 w-6"
                  style={{
                    filter:
                      "brightness(0) saturate(100%) invert(18%) sepia(95%) saturate(3028%) hue-rotate(346deg) brightness(90%) contrast(95%)",
                  }}
                />
                <h2 className="text-2xl font-bold">Lead Zeppelin</h2>
              </div>

              {/* AI Learning Instructions */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">AI Learning Instructions</h3>
                    <p className="text-sm text-gray-600">Real-time guidance from Lead Zeppelin AI</p>
                  </div>
                  <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                    Ready
                  </Badge>
                </div>

                <div className="bg-white rounded-lg p-4 border border-blue-100 min-h-[80px] flex items-center">
                  <p className="text-gray-700 text-center w-full">
                    {isPlaying && lessonSteps[currentStep]
                      ? lessonSteps[currentStep].instruction
                      : "Click 'Start Lesson' to begin receiving AI-powered learning instructions."}
                  </p>
                </div>
              </div>

              {/* Musical Note Haptic Feedback */}
              <div className="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-lg p-6 border border-emerald-200">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">Musical Note Feedback</h3>
                    <p className="text-sm text-gray-600">Visual and haptic response to your playing</p>
                  </div>
                  <Badge variant="secondary" className="bg-emerald-100 text-emerald-700">
                    Active
                  </Badge>
                </div>

                <div className="grid grid-cols-6 gap-2">
                  {notes.slice(0, 6).map((note, i) => (
                    <div
                      key={i}
                      className={`
                        h-12 rounded-lg border-2 transition-all duration-200 flex items-center justify-center font-bold text-sm
                        ${
                          activeNotes.includes(i)
                            ? "border-primary bg-primary text-primary-foreground shadow-lg animate-pulse"
                            : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
                        }
                      `}
                    >
                      {note}
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-6 gap-2 mt-2">
                  {notes.slice(6, 12).map((note, i) => (
                    <div
                      key={i + 6}
                      className={`
                        h-12 rounded-lg border-2 transition-all duration-200 flex items-center justify-center font-bold text-sm
                        ${
                          activeNotes.includes(i + 6)
                            ? "border-primary bg-primary text-primary-foreground shadow-lg animate-pulse"
                            : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
                        }
                      `}
                    >
                      {note}
                    </div>
                  ))}
                </div>
              </div>

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
                        Learning
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
                    {isPlaying && cameraPermission === "granted" ? (
                      <>
                        <video
                          ref={videoRef}
                          autoPlay
                          muted
                          className="absolute bottom-4 right-4 w-48 h-36 object-cover rounded border-2 border-white/50 z-10"
                        />

                        {/* Paper zone overlays with lesson highlighting */}
                        <div className="absolute inset-0 grid grid-cols-4 grid-rows-3 gap-1 p-4">
                          {Array.from({ length: 12 }, (_, i) => {
                            const isCurrentTarget =
                              lessonSteps[currentStep] && notes[i] === lessonSteps[currentStep].note
                            const isActive = activeNotes.includes(i)

                            return (
                              <div
                                key={i}
                                className={`
                                  border-2 border-dashed rounded transition-all duration-200
                                  ${
                                    isActive
                                      ? "border-primary bg-primary/20 shadow-lg"
                                      : isCurrentTarget
                                        ? "border-yellow-400 bg-yellow-400/20 animate-pulse"
                                        : "border-white/50"
                                  }
                                `}
                              >
                                {(isActive || isCurrentTarget) && (
                                  <div className="absolute inset-0 flex items-center justify-center">
                                    <Badge variant={isActive ? "default" : "secondary"} className="text-xs">
                                      {notes[i]}
                                    </Badge>
                                  </div>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      </>
                    ) : (
                      <div className="flex items-center justify-center h-full text-white/70">
                        <div className="text-center">
                          <Camera className="h-12 w-12 mx-auto mb-4 opacity-50" />
                          <p className="text-lg mb-2">Camera Feed</p>
                          <p className="text-sm">
                            {cameraPermission === "denied" ? "Camera access denied" : 'Click "Start Lesson" to begin'}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Lesson Steps Overview */}
              <Card>
                <CardHeader>
                  <CardTitle>Lesson Steps</CardTitle>
                  <CardDescription>Mary Had A Little Lamb - Note sequence</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-7 gap-2">
                    {lessonSteps.map((step, i) => (
                      <div
                        key={i}
                        className={`
                          h-16 rounded border-2 transition-all duration-200 flex flex-col items-center justify-center font-medium
                          ${
                            i < currentStep
                              ? "border-green-500 bg-green-500/20 text-green-700"
                              : i === currentStep
                                ? "border-primary bg-primary/20 text-primary animate-pulse"
                                : "border-border bg-card text-card-foreground"
                          }
                        `}
                      >
                        <span className="text-lg font-bold">{step.note}</span>
                        {i < currentStep && <CheckCircle className="h-3 w-3 text-green-500" />}
                        {i === currentStep && <Circle className="h-3 w-3 text-primary animate-pulse" />}
                      </div>
                    ))}
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
