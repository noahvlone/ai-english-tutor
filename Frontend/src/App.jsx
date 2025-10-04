import React from 'react'
import AudioWS from './AudioWS'
import Avatar from './Avatar'


export default function App(){
  return (
   <div style={{display:'flex', gap:20, padding:20}}>
     <div style={{width:360}}>
       <h2>AI English Tutor — Prototype</h2>
       <AudioWS />
     </div>
     <div>
       <Avatar />
     </div>
   </div>
  )
}
