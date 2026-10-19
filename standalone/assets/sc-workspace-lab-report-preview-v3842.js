/* Workspace 3.84.2 visual projection of an explicitly supplied Lab scene envelope.
   Never invents values and never persists or publishes data. */
export function mountLabScenePreview(container, scene) {
  if (!container || scene?.schemaName !== 'sc-lab-report-scene/1.0' || !Array.isArray(scene.frames) || !scene.frames.length) throw Error('Valid Lab scene required');
  container.replaceChildren();
  const heading=document.createElement('h3');heading.textContent=scene.title;
  const slider=document.createElement('input');slider.type='range';slider.min='0';slider.max=String(scene.frames.length-1);slider.value='0';slider.setAttribute('aria-label','Lab scene time frame');
  const info=document.createElement('p');const canvas=document.createElement('canvas');canvas.width=840;canvas.height=450;
  const caption=document.createElement('p');caption.textContent=`${scene.caption} — ${scene.provenance.assessment}; Lab ${scene.provenance.labObjectId}. 2D spatial projection only.`;
  function render(){
    const ctx=canvas.getContext('2d'); if(!ctx)return;
    ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);
    const frame=scene.frames[Number(slider.value)];info.textContent=`${scene.tLabel}: ${frame.time}`;
    const points=frame.points;if(!points.length)return;
    const xs=points.map(p=>p.x),ys=points.map(p=>p.y),xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);
    ctx.fillStyle='#111';ctx.font='14px sans-serif';ctx.fillText(scene.xLabel,400,435);ctx.fillText(scene.yLabel,10,26);
    ctx.strokeStyle='#111';ctx.beginPath();ctx.moveTo(65,45);ctx.lineTo(65,410);ctx.lineTo(810,410);ctx.stroke();
    const px=p=>65+735*(p.x-xmin)/(xmax-xmin||1),py=p=>410-355*(p.y-ymin)/(ymax-ymin||1);
    ctx.strokeStyle='#aa182b';ctx.fillStyle='#aa182b';ctx.beginPath();points.forEach((p,i)=>{const x=px(p),y=py(p);if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y)});ctx.stroke();
    for(const p of points){ctx.beginPath();ctx.arc(px(p),py(p),3,0,2*Math.PI);ctx.fill()}
  }
  slider.addEventListener('input',render);container.append(heading,slider,info,canvas,caption);render();
  return {destroy(){container.replaceChildren()}};
}
