#!/usr/bin/env bash
# Best-in-class-per-OS audible alert that the human is needed. Not lowest-common-
# denominator: each platform uses its richest available channel (chime + speech).
# Usage: notify-human.sh "message to speak/show"
msg="${*:-Claude needs you}"
case "$(uname -s)" in
  Darwin)   # macOS: distinctive chime + spoken message + Notification Center banner
    afplay /System/Library/Sounds/Glass.aiff 2>/dev/null
    say -v Samantha "$msg" 2>/dev/null
    osascript -e "display notification \"$msg\" with title \"Claude needs you\" sound name \"Glass\"" 2>/dev/null ;;
  Linux)    # PulseAudio/Canberra chime + speech-dispatcher/espeak; notify-send banner
    { canberra-gtk-play -i dialog-information 2>/dev/null || paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || printf '\a'; }
    { spd-say "$msg" 2>/dev/null || espeak "$msg" 2>/dev/null; }
    notify-send "Claude needs you" "$msg" 2>/dev/null ;;
  MINGW*|MSYS*|CYGWIN*)  # Windows via Git-Bash: SystemSound + SAPI speech + toast-ish
    powershell.exe -NoProfile -Command "[System.Media.SystemSounds]::Exclamation.Play(); Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('$msg')" 2>/dev/null ;;
  *) printf '\a' ;;
esac
