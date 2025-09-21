'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Play, Pause, Camera, CameraOff, Volume2, ChevronDown, ChevronUp, Settings, Search } from "lucide-react"
import Navbar from "@/components/navbar"

export default function LiveDemo() {
  const [selectedInstrument, setSelectedInstrument] = useState("piano")
  const [selectedLesson, setSelectedLesson] = useState("song-x-artist")
  const [isPlaying, setIsPlaying] = useState(false)
  const [cameraEnabled, setCameraEnabled] = useState(false)
  const [audioVolume, setAudioVolume] = useState([85])
  const [playedNotes, setPlayedNotes] = useState(['C', 'E', 'F'])
  const [nextNotes] = useState(['G', 'A', 'B', 'C'])
  const [currentSong, setCurrentSong] = useState("Song X - Artist")
  const [sheetMusicUrl, setSheetMusicUrl] = useState("")
  const [lessonSearchTerm, setLessonSearchTerm] = useState("")
  
  // Collapsible states - ADVANCED MENU HIDDEN BY DEFAULT
  const [isPlaybackOpen, setIsPlaybackOpen] = useState(true)
  const [isCameraOpen, setIsCameraOpen] = useState(true)
  const [isAdvancedMenuOpen, setIsAdvancedMenuOpen] = useState(false)
  
  // Advanced settings
  const [numberOfSquares, setNumberOfSquares] = useState(8)
  const [selectedScale, setSelectedScale] = useState("major")

  const videoRef = useRef<HTMLVideoElement>(null)
  const notesScrollRef = useRef<HTMLDivElement>(null)

  // Only Piano, Flute, and Drums with emojis
  const instruments = [
    { value: "piano", label: "🎹 Piano" },
    { value: "flute", label: "🪈 Flute" },
    { value: "drums", label: "🥁 Drums" }
  ]

  // Comprehensive musical scales
  const getScaleOptions = (instrument: string) => {
    switch (instrument) {
      case "piano":
        return [
          { value: "major", label: "Major Scale" },
          { value: "minor", label: "Natural Minor Scale" },
          { value: "harmonic-minor", label: "Harmonic Minor Scale" },
          { value: "melodic-minor", label: "Melodic Minor Scale" },
          { value: "pentatonic-major", label: "Major Pentatonic Scale" },
          { value: "pentatonic-minor", label: "Minor Pentatonic Scale" },
          { value: "blues-major", label: "Major Blues Scale" },
          { value: "blues-minor", label: "Minor Blues Scale" },
          { value: "chromatic", label: "Chromatic Scale" },
          { value: "whole-tone", label: "Whole Tone Scale" },
          { value: "dorian", label: "Dorian Mode" },
          { value: "phrygian", label: "Phrygian Mode" },
          { value: "lydian", label: "Lydian Mode" },
          { value: "mixolydian", label: "Mixolydian Mode" }
        ]
      case "flute":
        return [
          { value: "major", label: "Major Scale" },
          { value: "minor", label: "Natural Minor Scale" },
          { value: "harmonic-minor", label: "Harmonic Minor Scale" },
          { value: "melodic-minor", label: "Melodic Minor Scale" },
          { value: "pentatonic-major", label: "Major Pentatonic Scale" },
          { value: "pentatonic-minor", label: "Minor Pentatonic Scale" },
          { value: "chromatic", label: "Chromatic Scale" },
          { value: "whole-tone", label: "Whole Tone Scale" },
          { value: "dorian", label: "Dorian Mode" },
          { value: "phrygian", label: "Phrygian Mode" },
          { value: "lydian", label: "Lydian Mode" },
          { value: "mixolydian", label: "Mixolydian Mode" }
        ]
      case "drums":
        return [
          { value: "single-stroke-roll", label: "Single Stroke Roll" },
          { value: "double-stroke-roll", label: "Double Stroke Roll" },
          { value: "paradiddle", label: "Single Paradiddle" },
          { value: "flam", label: "Flam" },
          { value: "drag", label: "Drag" },
          { value: "five-stroke-roll", label: "5 Stroke Roll" },
          { value: "seven-stroke-roll", label: "7 Stroke Roll" },
          { value: "nine-stroke-roll", label: "9 Stroke Roll" },
          { value: "flamacue", label: "Flamacue" },
          { value: "ruff", label: "Ruff" }
        ]
      default:
        return [{ value: "major", label: "Major Scale" }]
    }
  }

  // Lesson list
  const lessons = [
    { value: "song-x-artist", label: "Song X - Artist", artist: "Various Artists" },
    { value: "twinkle-star", label: "Twinkle Little Star", artist: "Traditional" },
    { value: "happy-birthday", label: "Happy Birthday", artist: "Traditional" },
    { value: "mary-lamb", label: "Mary Had a Little Lamb", artist: "Traditional" },
    { value: "ode-joy", label: "Ode to Joy", artist: "Beethoven" },
    { value: "fur-elise", label: "Für Elise", artist: "Beethoven" },
    { value: "canon-d", label: "Canon in D", artist: "Pachelbel" },
    { value: "moonlight", label: "Moonlight Sonata", artist: "Beethoven" },
    { value: "amazing-grace", label: "Amazing Grace", artist: "Traditional" },
    { value: "somewhere-rainbow", label: "Somewhere Over the Rainbow", artist: "Judy Garland" }
  ]

  // Filter lessons based on search term
  const filteredLessons = lessons.filter(lesson =>
    lesson.label.toLowerCase().includes(lessonSearchTerm.toLowerCase()) ||
    lesson.artist.toLowerCase().includes(lessonSearchTerm.toLowerCase())
  )

  // Simulate real-time note playing
  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setPlayedNotes(prev => {
          const newNote = nextNotes[Math.floor(Math.random() * nextNotes.length)]
          const updated = [...prev, newNote]
          
          setTimeout(() => {
            if (notesScrollRef.current) {
              notesScrollRef.current.scrollLeft = notesScrollRef.current.scrollWidth
            }
          }, 100)
          
          return updated.slice(-10)
        })
      }, 2000)
      
      return () => clearInterval(interval)
    }
  }, [isPlaying, nextNotes])

  const enableCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
      setCameraEnabled(true)
    } catch (error) {
      console.error('Camera access denied:', error)
    }
  }

  const disableCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks()
      tracks.forEach(track => track.stop())
      videoRef.current.srcObject = null
    }
    setCameraEnabled(false)
  }

  const toggleCamera = () => cameraEnabled ? disableCamera() : enableCamera()
  const togglePlayback = () => setIsPlaying(!isPlaying)
  
  const handleCustomizeLayout = () => {
    setIsAdvancedMenuOpen(!isAdvancedMenuOpen)
  }

  return (
    <div className="h-screen bg-background overflow-hidden flex flex-col">
      {/* NAVBAR */}
      <Navbar />
      
      {/* MAIN CONTENT - NO SCROLLING */}
      <div className="flex-1 p-4 overflow-hidden">
        {/* Compact Header */}
        <div className="mb-4">
          <h1 className="text-2xl font-bold mb-1">Live Demo</h1>
          <p className="text-sm text-muted-foreground">
            Experience real-time paper-to-MIDI conversion with visual feedback and multiple instrument sounds.
          </p>
        </div>

        {/* FIXED HEIGHT LAYOUT - FITS SCREEN PERFECTLY */}
        <div className="grid grid-cols-12 gap-4 h-[calc(100vh-200px)]">
          
          {/* LEFT COLUMN - 3 columns wide */}
          <div className="col-span-12 lg:col-span-3 flex flex-col space-y-3 min-h-0">
            
            {/* BOX 1: Currently Playing */}
            <Card className="flex-shrink-0">
              <CardHeader className="pb-2 py-3">
                <CardTitle className="text-base">Currently Playing:</CardTitle>
              </CardHeader>
              <CardContent className="pt-0 pb-3">
                <Select value={selectedInstrument} onValueChange={setSelectedInstrument}>
                  <SelectTrigger className="w-full h-9">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {instruments.map((instrument) => (
                      <SelectItem key={instrument.value} value={instrument.value}>
                        {instrument.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* BOX 2: Playback */}
            <Card className="flex-shrink-0">
              <CardHeader 
                className="pb-2 py-3 cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => setIsPlaybackOpen(!isPlaybackOpen)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-base">Playback</CardTitle>
                    <p className="text-xs text-muted-foreground">Start or Stop Demo</p>
                  </div>
                  {isPlaybackOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </div>
              </CardHeader>
              {isPlaybackOpen && (
                <CardContent className="pt-0 pb-3 space-y-3">
                  <Button
                    onClick={togglePlayback}
                    variant={isPlaying ? "destructive" : "default"}
                    size="sm"
                    className="w-full"
                  >
                    {isPlaying ? (
                      <>
                        <Pause className="mr-2 h-3 w-3" />
                        Stop Demo
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-3 w-3" />
                        Start Demo
                      </>
                    )}
                  </Button>
                  
                  {/* Audio Volume Section */}
                  <div className="border-t pt-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Volume2 className="h-3 w-3" />
                      <Label className="text-sm font-medium">Audio Volume</Label>
                    </div>
                    <Slider
                      value={audioVolume}
                      onValueChange={setAudioVolume}
                      max={100}
                      step={1}
                      className="w-full"
                    />
                    <div className="text-center text-xs text-muted-foreground mt-1">
                      {audioVolume[0]}%
                    </div>
                  </div>
                </CardContent>
              )}
            </Card>

            {/* BOX 3: Camera */}
            <Card className="flex-1 flex flex-col min-h-0">
              <CardHeader 
                className="pb-2 py-3 cursor-pointer hover:bg-muted/50 transition-colors flex-shrink-0"
                onClick={() => setIsCameraOpen(!isCameraOpen)}
              >
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Camera className="h-4 w-4" />
                    Camera
                  </CardTitle>
                  {isCameraOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </div>
              </CardHeader>
              {isCameraOpen && (
                <CardContent className="pt-0 pb-3 flex-1 flex flex-col min-h-0">
                  <div className="flex items-center space-x-2 mb-3 flex-shrink-0">
                    <Switch
                      checked={cameraEnabled}
                      onCheckedChange={toggleCamera}
                    />
                    <Label className="text-sm">Enable Camera</Label>
                  </div>
                  
                  {/* Spacer */}
                  <div className="flex-1 min-h-0" />
                  
                  <div className="border-t pt-3 space-y-2 flex-shrink-0">
                    <Button 
                      onClick={handleCustomizeLayout}
                      variant="secondary"
                      size="sm"
                      className="w-full"
                    >
                      <Settings className="mr-2 h-3 w-3" />
                      Customize your layout!
                    </Button>
                    <p className="text-xs text-muted-foreground text-center">
                      *Advanced*
                    </p>

                    {/* Advanced Menu */}
                    {isAdvancedMenuOpen && (
                      <div className="bg-muted/50 rounded-lg p-3 space-y-3 border">
                        <div>
                          <Label className="text-xs font-medium">Number of Squares</Label>
                          <div className="flex items-center space-x-2 mt-1">
                            <Slider
                              value={[numberOfSquares]}
                              onValueChange={(value) => setNumberOfSquares(value[0])}
                              min={4}
                              max={16}
                              step={1}
                              className="flex-1"
                            />
                            <span className="text-xs w-8 text-center">{numberOfSquares}</span>
                          </div>
                        </div>
                        
                        <div>
                          <Label className="text-xs font-medium">Musical Scale/Set</Label>
                          <Select value={selectedScale} onValueChange={setSelectedScale}>
                            <SelectTrigger className="w-full h-8 mt-1">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {getScaleOptions(selectedInstrument).map((scale) => (
                                <SelectItem key={scale.value} value={scale.value}>
                                  {scale.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    )}
                    
                    <Button 
                      onClick={toggleCamera}
                      variant="outline" 
                      size="sm"
                      className="w-full"
                    >
                      🎵 Start Playing
                    </Button>
                  </div>
                </CardContent>
              )}
            </Card>
          </div>

          {/* MIDDLE COLUMN - 3 columns wide */}
          <div className="col-span-12 lg:col-span-3 flex flex-col space-y-3 min-h-0">
            
            {/* LESSONS BOX - ONLY INTERNAL SCROLLING */}
            <Card className="flex-1 flex flex-col min-h-0">
              <CardHeader className="pb-2 py-3 flex-shrink-0">
                <CardTitle className="text-base">Lesson:</CardTitle>
                <div className="relative">
                  <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-3 w-3 text-muted-foreground" />
                  <Input
                    placeholder="Search lessons..."
                    value={lessonSearchTerm}
                    onChange={(e) => setLessonSearchTerm(e.target.value)}
                    className="pl-8 h-8 text-sm"
                  />
                </div>
              </CardHeader>
              <CardContent className="pt-0 pb-3 flex-1 min-h-0">
                <div className="h-full overflow-y-auto pr-2 space-y-2">
                  {filteredLessons.map((lesson) => (
                    <div
                      key={lesson.value}
                      onClick={() => setSelectedLesson(lesson.value)}
                      className={`p-2 rounded border cursor-pointer transition-colors text-sm hover:bg-muted/50 ${
                        selectedLesson === lesson.value 
                          ? 'bg-red-50 border-red-500 border-2'
                          : 'bg-card border-border'
                      }`}
                    >
                      <div className={`font-medium text-sm ${
                        selectedLesson === lesson.value ? 'text-red-700' : ''
                      }`}>
                        {lesson.label}
                      </div>
                      <div className={`text-xs ${
                        selectedLesson === lesson.value ? 'text-red-600' : 'text-muted-foreground'
                      }`}>
                        {lesson.artist}
                      </div>
                    </div>
                  ))}
                  {filteredLessons.length === 0 && (
                    <div className="text-center text-sm text-muted-foreground py-8">
                      No lessons found matching "{lessonSearchTerm}"
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* URL BOX */}
            <Card className="flex-shrink-0">
              <CardHeader className="pb-2 py-3">
                <CardTitle className="text-base">Retrieve Sheet Music</CardTitle>
              </CardHeader>
              <CardContent className="pt-0 pb-3 space-y-2">
                <div>
                  <Label className="text-xs">URL:</Label>
                  <Input
                    placeholder="http://......net/music"
                    value={sheetMusicUrl}
                    onChange={(e) => setSheetMusicUrl(e.target.value)}
                    className="mt-1 h-8 text-sm"
                  />
                </div>
                <Button variant="outline" size="sm" className="w-full">
                  Retrieve Sheet Music
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* RIGHT COLUMN - 6 columns wide (LARGER FOR CAMERA) */}
          <div className="col-span-12 lg:col-span-6 min-h-0">
            <Card className="h-full flex flex-col">
              <CardHeader className="pb-2 py-3 flex-shrink-0">
                <CardTitle className="text-base">Currently Playing: {currentSong}</CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col space-y-3 overflow-hidden p-3">
                
                {/* LARGE CAMERA FEED */}
                <div className="flex-1 min-h-0">
                  <div className="h-full bg-muted rounded-lg flex items-center justify-center relative overflow-hidden">
                    {cameraEnabled ? (
                      <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        className="w-full h-full object-cover rounded-lg"
                      />
                    ) : (
                      <div className="text-center p-6">
                        <Camera className="mx-auto h-16 w-16 text-muted-foreground mb-4" />
                        <h3 className="text-xl font-semibold mb-2">Live Feed Here</h3>
                        <p className="text-sm text-muted-foreground mb-1">
                          Camera resolution: 1920x1080 (16:9)
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Enable camera to start
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* NEXT NOTE SECTION */}
                <div className="flex-shrink-0 border-t pt-2">
                  <h4 className="text-sm font-medium mb-2">Next Note:</h4>
                  <div 
                    ref={notesScrollRef}
                    className="flex space-x-1 overflow-x-auto pb-1"
                    style={{ scrollBehavior: 'smooth' }}
                  >
                    {playedNotes.map((note, index) => (
                      <div
                        key={`played-${index}`}
                        className="flex-shrink-0 w-8 h-8 border rounded flex items-center justify-center text-xs font-bold bg-green-100 text-green-800 border-green-300"
                      >
                        {note}
                      </div>
                    ))}
                    
                    {nextNotes.slice(0, 4).map((note, index) => (
                      <div
                        key={`next-${index}`}
                        className={`flex-shrink-0 w-8 h-8 border rounded flex items-center justify-center text-xs font-bold ${
                          index === 0 
                            ? 'bg-blue-100 text-blue-800 border-blue-300' 
                            : 'bg-muted border-muted-foreground/20'
                        }`}
                      >
                        {note}
                      </div>
                    ))}
                  </div>
                </div>

                {/* AI FEEDBACK */}
                <div className="flex-shrink-0 border-t pt-2">
                  <h4 className="text-sm font-medium mb-2">*AI teacher feedback goes here*</h4>
                  <div className="p-2 bg-muted/50 rounded text-xs text-muted-foreground">
                    {isPlaying 
                      ? "Great job! Keep maintaining steady rhythm." 
                      : "Start the demo to receive AI guidance."
                    }
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}