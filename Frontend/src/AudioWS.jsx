import React, {useRef, useState} from 'react'


export default function AudioWS(){
  const wsRef = useRef(null)
  const mediaRef = useRef(null)
  const [recording, setRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [reply, setReply] = useState('')


async function connect(){
  if(wsRef.current) return
  const ws = new WebSocket((location.hostname==='localhost'? 'ws://':'wss://') + window.
