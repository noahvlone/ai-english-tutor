import React, {useEffect, useState, useRef} from 'react'


export default function Avatar(){
  const [mouth, setMouth] = useState(0)
  const mouthRef = useRef(0)


// listen for custom event 'avatar:mouth' to animate mouth
useEffect(()=>{
  function onM(e){
    const v = e.detail || 0
    setMouth(v)
    mouthRef.current = v
  }
  window.addEventListener('avatar:mouth', onM)
  return ()=> window.removeEventListener('avatar:mouth', onM)
},[])


return (
  <div style={{width:300,height:400,display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column',border:'1px solid #ddd',padding:20,borderRadius:12}}>
    <div style={{width:180,height:180,background:'#f6f6f8',borderRadius:'50%',display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',position:'relative'}}>
      <div style={{position:'absolute',top:40,display:'flex',gap:20}}>
        <div style={{width:20,height:20,background:'#222',borderRadius:10}}></div>
        <div style={{width:20,height:20,background:'#222',borderRadius:10}}></div>
      </div>
      <div style={{position:'absolute',bottom:30,width:100,height:20,background:'#fff',borderRadius:10,overflow:'hidden',display:'flex',alignItems:'center',justifyContent:'center'}}>
        <div style={{width:60,height:Math.max(4, mouth*20), background:'#e33', borderRadius:8, transition:'height 80ms linear'}}></div>
      </div>
    </div>
    <p style={{marginTop:12}}>Tutor Avatar</p>
  </div>
 )
}
