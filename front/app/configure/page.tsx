"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Camera, Volume2, Zap, ArrowLeft, BookOpen } from "lucide-react"
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

export default function ConfigurePage() {
  const [cameraEnabled, setCameraEnabled] = useState(false)
  const [selectedZones, setSelectedZones] = useState<number[]>([])
  const [zoneNotes, setZoneNotes] = useState<{ [key: number]: string }>({})
  const [showPresetMenu, setShowPresetMenu] = useState(true)
  const [showLearnAnySong, setShowLearnAnySong] = useState(false)
  const [songUrl, setSongUrl] = useState("")
  const [autoMappedZones, setAutoMappedZones] = useState<{ [key: number]: string }>({})
  const [selectedInstrument, setSelectedInstrument] = useState("piano")
  const router = useRouter()

  const notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

  const instruments = [
    { value: "piano", label: "Piano", icon: <LeadZeppelinLogo size={20} /> },
    { value: "guitar", label: "Guitar", icon: <LeadZeppelinLogo size={20} />, toBe: true },
    { value: "violin", label: "Violin", icon: <LeadZeppelinLogo size={20} />, toBe: true },
    { value: "drums", label: "Drums", icon: <LeadZeppelinLogo size={20} />, toBe: true },
    { value: "flute", label: "Flute", icon: <LeadZeppelinLogo size={20} />, toBe: true },
    { value: "saxophone", label: "Saxophone", icon: <LeadZeppelinLogo size={20} />, toBe: true },
  ]

  const analyzeSongAndMapZones = (url: string) => {
    // This would be replaced with actual backend integration
    if (url.includes("mary-had-a-little-lamb") || url.toLowerCase().includes("mary")) {
      setAutoMappedZones({
        0: "E",
        1: "D",
        2: "C",
      })
    } else if (url.includes("twinkle") || url.toLowerCase().includes("twinkle")) {
      setAutoMappedZones({
        0: "C",
        1: "D",
        2: "E",
        3: "F",
        4: "G",
      })
    } else {
      // Default mapping for unknown songs
      setAutoMappedZones({
        0: "C",
        1: "D",
        2: "E",
        3: "F",
      })
    }
  }

  const handleSongUrlChange = (url: string) => {
    setSongUrl(url)
    if (url.trim()) {
      analyzeSongAndMapZones(url)
    } else {
      setAutoMappedZones({})
    }
  }

  const toggleZone = (zoneId: number) => {
    if (zoneNotes[zoneId]) {
      const newZoneNotes = { ...zoneNotes }
      delete newZoneNotes[zoneId]
      setZoneNotes(newZoneNotes)
      setSelectedZones((prev) => prev.filter((id) => id !== zoneId))
    }
  }

  const handleNoteSelect = (zoneId: number, note: string) => {
    setZoneNotes((prev) => ({ ...prev, [zoneId]: note }))
    if (!selectedZones.includes(zoneId)) {
      setSelectedZones((prev) => [...prev, zoneId])
    }
  }

  const getAvailableNotes = (currentZoneId: number) => {
    const assignedNotes = Object.entries(zoneNotes)
      .filter(([zoneId]) => Number.parseInt(zoneId) !== currentZoneId)
      .map(([, note]) => note)
    return notes.filter((note) => !assignedNotes.includes(note))
  }

  const selectPreset = (presetName: string) => {
    console.log(`Loading preset: ${presetName}`)
    router.push("/demo")
  }

  const handleLearnAnySong = () => {
    setShowLearnAnySong(true)
    setShowPresetMenu(false)
  }

  const handleBackToPresets = () => {
    setShowLearnAnySong(false)
    setShowPresetMenu(true)
  }

  return (
    <div className="min-h-screen bg-background">
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
          <h1 className="text-3xl font-bold mb-2">Instrument Settings</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Camera className="h-5 w-5" />
                  Camera Settings
                </CardTitle>
                <CardDescription>Configure camera detection settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="camera-toggle">Enable Camera</Label>
                  <Switch id="camera-toggle" checked={cameraEnabled} onCheckedChange={setCameraEnabled} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {!showLearnAnySong && showPresetMenu && (
                  <Button className="w-full bg-transparent" variant="outline" onClick={handleLearnAnySong}>
                    <BookOpen className="h-4 w-4 mr-2" />
                    Learn Any Song
                  </Button>
                )}
                <Button
                  className="w-full bg-transparent"
                  variant="outline"
                  onClick={() => {
                    if (showLearnAnySong) {
                      handleBackToPresets()
                    } else {
                      setShowPresetMenu(!showPresetMenu)
                    }
                  }}
                >
                  {showLearnAnySong ? (
                    "Back to Lessons"
                  ) : showPresetMenu ? (
                    <>
                      Customize your layout! <span className="text-red-500 font-bold">**ADVANCED**</span>
                    </>
                  ) : (
                    "Load Preset"
                  )}
                </Button>
                <Separator />
                <Link href="/demo" className="w-full">
                  <Button className="w-full">
                    <Volume2 className="h-4 w-4 mr-2" />
                    Start Playing
                  </Button>
                </Link>
              </CardContent>
            </Card>

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
          </div>

          <div className="lg:col-span-2">
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {showLearnAnySong ? (
                    <>
                      <ArrowLeft className="h-5 w-5 cursor-pointer" onClick={handleBackToPresets} />
                      Learn Any Song
                    </>
                  ) : showPresetMenu ? (
                    "Lead Zeppelin Lessons"
                  ) : (
                    <>
                      <ArrowLeft className="h-5 w-5 cursor-pointer" onClick={() => setShowPresetMenu(true)} />
                      Paper Zone Layout
                    </>
                  )}
                </CardTitle>
                <CardDescription>
                  {showLearnAnySong
                    ? "Use Lead Zeppelin and Google Gemini to learn any song!"
                    : showPresetMenu
                      ? "Select a preset configuration to get started quickly"
                      : "Click zones to assign musical notes. Selected zones will be highlighted."}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {showLearnAnySong ? (
                  <div className="space-y-6">
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="song-url" className="text-base font-medium">
                          Song URL
                        </Label>
                        <Input
                          id="song-url"
                          type="url"
                          placeholder="https://www.noobnotes.net/..."
                          value={songUrl}
                          onChange={(e) => handleSongUrlChange(e.target.value)}
                          className="mt-2"
                        />
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Copy and Paste any song URL from NoobNotes.Net to start your learning!
                      </p>
                    </div>

                    <Button className="w-full" disabled={!songUrl.trim()}>
                      <BookOpen className="h-4 w-4 mr-2" />
                      Start Learning This Song
                    </Button>

                    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                        <LeadZeppelinLogo size={16} />
                        Auto-Mapped Zones for This Song
                      </h4>
                      {Object.keys(autoMappedZones).length > 0 ? (
                        <>
                          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                            {Object.entries(autoMappedZones).map(([zoneId, note]) => (
                              <div
                                key={zoneId}
                                className="flex items-center justify-between bg-white p-3 rounded border"
                              >
                                <span className="text-sm font-medium text-gray-700">
                                  Zone {Number.parseInt(zoneId) + 1}
                                </span>
                                <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                                  {note}
                                </Badge>
                              </div>
                            ))}
                          </div>
                          <p className="text-xs text-blue-600 mt-3">
                            These zones have been automatically configured based on the song's musical requirements.
                          </p>
                        </>
                      ) : (
                        <p className="text-sm text-gray-600">
                          Enter a song URL above to see the automatic zone mapping for that song.
                        </p>
                      )}
                    </div>
                  </div>
                ) : showPresetMenu ? (
                  <div className="space-y-4">
                    <div className="grid gap-4">
                      <Button
                        variant="outline"
                        className="h-auto p-6 text-left justify-start bg-transparent"
                        onClick={() => selectPreset("Mary Had A Little Lamb")}
                      >
                        <div>
                          <div className="font-semibold text-base mb-1">Learn How To Play Mary Had A Little Lamb</div>
                          <div className="text-sm text-muted-foreground">
                            Simple 3-note configuration perfect for beginners
                          </div>
                        </div>
                      </Button>

                      <Button
                        variant="outline"
                        className="h-auto p-6 text-left justify-start bg-transparent"
                        onClick={() => selectPreset("Twinkle Twinkle")}
                      >
                        <div>
                          <div className="font-semibold text-base mb-1">Twinkle Twinkle Little Star</div>
                          <div className="text-sm text-muted-foreground">Classic nursery rhyme with 5-note range</div>
                        </div>
                      </Button>

                      <Button
                        variant="outline"
                        className="h-auto p-6 text-left justify-start bg-transparent"
                        onClick={() => selectPreset("Happy Birthday")}
                      >
                        <div>
                          <div className="font-semibold text-base mb-1">Happy Birthday</div>
                          <div className="text-sm text-muted-foreground">Celebrate with this 6-note birthday song</div>
                        </div>
                      </Button>

                      <Button
                        variant="outline"
                        className="h-auto p-6 text-left justify-start bg-transparent"
                        onClick={() => selectPreset("Full Scale")}
                      >
                        <div>
                          <div className="font-semibold text-base mb-1">Full Chromatic Scale</div>
                          <div className="text-sm text-muted-foreground">
                            Complete 12-note setup for advanced playing
                          </div>
                        </div>
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="relative bg-card border-2 border-dashed border-border rounded-lg p-8 min-h-[500px]">
                      <div className="relative w-full h-full bg-white border border-gray-300 rounded shadow-sm">
                        <div className="grid grid-cols-4 grid-rows-3 gap-2 p-4 h-full">
                          {Array.from({ length: 12 }, (_, i) => (
                            <div
                              key={i}
                              className={`
                                relative border-2 border-dashed rounded-lg p-4 transition-all duration-200
                                ${
                                  zoneNotes[i]
                                    ? "border-gray-400 bg-gray-100/50 shadow-md"
                                    : "border-transparent bg-transparent hover:border-gray-300/50"
                                }
                              `}
                            >
                              <div className="text-center">
                                <div className="text-sm font-medium text-gray-600 mb-2">Zone {i + 1}</div>
                                {zoneNotes[i] ? (
                                  <div className="space-y-2">
                                    <Badge variant="secondary" className="text-xs">
                                      {zoneNotes[i]}
                                    </Badge>
                                    <Button
                                      size="sm"
                                      variant="outline"
                                      className="w-full text-xs bg-transparent"
                                      onClick={() => toggleZone(i)}
                                    >
                                      Reset
                                    </Button>
                                  </div>
                                ) : (
                                  <Select onValueChange={(note) => handleNoteSelect(i, note)}>
                                    <SelectTrigger className="w-full h-8 text-xs">
                                      <SelectValue placeholder="Select note" />
                                    </SelectTrigger>
                                    <SelectContent>
                                      {getAvailableNotes(i).map((note) => (
                                        <SelectItem key={note} value={note} className="text-xs">
                                          {note}
                                        </SelectItem>
                                      ))}
                                    </SelectContent>
                                  </Select>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 p-4 bg-muted rounded-lg">
                      <h4 className="font-medium mb-2">Selected Zones ({Object.keys(zoneNotes).length}/12)</h4>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(zoneNotes).map(([zoneId, note]) => (
                          <Badge key={zoneId} variant="outline">
                            Zone {Number.parseInt(zoneId) + 1}: {note}
                          </Badge>
                        ))}
                      </div>
                      {Object.keys(zoneNotes).length === 0 && (
                        <p className="text-sm text-muted-foreground">Click on zones above to assign musical notes</p>
                      )}
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
