// Execute the actual page callback and timer with a small DOM/clock fixture.
const fs=require('fs'), path=require('path'), vm=require('vm'), assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../study/Task.html'),'utf8');

function bodyAfter(marker) {
    const start=source.indexOf(marker);
    assert.ok(start>=0, 'page function exists: '+marker);
    const brace=source.indexOf('{',start);
    let depth=0;
    for(let i=brace;i<source.length;i++) {
        if(source[i]==='{') depth++;
        if(source[i]==='}' && --depth===0) return source.slice(brace,i+1);
    }
    throw Error('Unclosed page function');
}
function setup(doIdeal=1) {
    const elements=new Map(); let now=0;
    const el=id=>{
        if(!elements.has(id)) elements.set(id,{value:'',innerText:'',style:{},classList:{add(){},remove(){}},clicks:0,click(){this.clicks++;},focus(){}});
        return elements.get(id);
    };
    const context={document:{getElementById:el}, performance:{now:()=>now},
        taskClient:{pending:null}, js_vars:{do_ideal:doIdeal}, serverRemaining:null,
        receivedAt:0, taskCompleted:false, taskSecondsLeft:Infinity, videosStarted:false,
        disableTaskInputs(){}, startBreakVideos(){context.videos=(context.videos||0)+1;},
    };
    vm.createContext(context);
    vm.runInContext('function onState(data, changedTask) '+bodyAfter('onState(data, changedTask)')+
        '\nfunction seconds_left() '+bodyAfter('function seconds_left()')+
        '\nfunction formatTime(seconds) '+bodyAfter('function formatTime(seconds)')+
        '\nfunction tick() '+bodyAfter('function tick()'),context);
    const state={performance:0,mistakes:0,work_seconds:0,remaining_seconds:480,completed:true,stopped_work:true};
    return {c:context,state,el,advance(ms){now+=ms;context.tick();}};
}
{
    const t=setup(); t.c.onState(t.state,false);
    assert.equal(t.c.taskCompleted,true,'zero target is complete at initial load');
    assert.equal(t.c.videos,1); assert.equal(t.el('next-button').clicks,0,'completion must not skip the leisure period');
    t.advance(479000); assert.equal(t.el('next-button').clicks,0);
    t.advance(1000); assert.equal(t.el('next-button').clicks,1,'zero ideal advances at original deadline');
}
{
    const t=setup(); t.c.onState({...t.state,remaining_seconds:280},false);
    t.advance(279000); assert.equal(t.el('next-button').clicks,0);
    t.advance(1000); assert.equal(t.el('next-button').clicks,1,'refresh uses server remainder, not a new full period');
}
{
    const t=setup(); t.c.onState({...t.state,remaining_seconds:0},false);
    assert.equal(t.el('next-button').clicks,1,'late refresh advances a completed zero ideal');
}
{
    const t=setup(); t.c.onState({...t.state,completed:false,stopped_work:false,remaining_seconds:0},false);
    t.c.tick(); assert.equal(t.el('next-button').clicks,0,'unfinished positive ideal remains open after deadline');
    assert.match(t.el('task-timer').innerText,/remaining tasks/);
}
{
    const t=setup(); t.c.onState({...t.state,performance:1,work_seconds:10,remaining_seconds:470},false);
    assert.equal(t.c.taskCompleted,true); assert.equal(t.c.videos,1);
    t.advance(470000); assert.equal(t.el('next-button').clicks,1,'positive early completion still waits for deadline');
}
{
    const t=setup(); t.c.onState({...t.state,performance:1,work_seconds:480,remaining_seconds:0},false);
    assert.equal(t.el('next-button').clicks,1,'positive overtime completion still advances immediately');
}
{
    const t=setup(0); t.c.onState({...t.state,completed:false},false);
    t.advance(480000); assert.equal(t.el('next-button').clicks,1,'free-choice zero-second stop advances normally');
}
console.log('7 actual-page completion/timer cases passed: zero, refresh, late refresh, positive early/overtime, unfinished ideal, immediate free stop.');
