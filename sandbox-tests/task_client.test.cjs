const fs = require('fs');
const vm = require('vm');
const assert = require('node:assert/strict');
const path = require('path');
const source = fs.readFileSync(path.join(__dirname, '../_static/task_client.js'), 'utf8');

function setup(storage = new Map()) {
    const sent = [], timers = new Map(), busy = [];
    let nextTimer = 0, failSend = false;
    const context = {
        sessionStorage: {getItem: k => storage.get(k) ?? null, setItem: (k,v) => storage.set(k,v), removeItem: k => storage.delete(k)},
        liveSend(message) { if (failSend) throw Error('offline'); sent.push(structuredClone(message)); },
        setTimeout(fn) { timers.set(++nextTimer, fn); return nextTimer; },
        clearTimeout(id) { timers.delete(id); },
    };
    vm.createContext(context);
    vm.runInContext(source + '\nthis.TaskClient = TaskClient;', context);
    const client = new context.TaskClient({storageKey: 'participant-A-round-2', getAnswer: () => [101,102,103,104],
        setBusy(value) { busy.push(value); }, onState() {}});
    const state = {task_id: 'word-1', answer_token: 'attempt-1', revision: 0, performance: 0, stopped_work: false, completed: false};
    return {client, state, sent, storage, busy, offline(value) { failSend = value; },
        retry() { const callbacks = [...timers.values()]; timers.clear(); callbacks.forEach(fn => fn()); }};
}

{
    const t = setup(); t.client.receive(t.state); t.client.submit(); t.client.submit();
    assert.equal(t.sent.length, 1, 'double click submits only once while pending');
    assert.equal(t.client.state.performance, 0, 'browser does not optimistically increase total');
    t.retry();
    assert.deepEqual(t.sent[0], t.sent[1], 'lost reply retries identical server token');
    t.client.receive({...t.state, task_id:'word-2', answer_token:'attempt-2', performance:1, revision:1, reply_to:'attempt-1'});
    assert.equal(t.client.pending, null);
    assert.equal(t.storage.size, 0);
    t.client.submit(); assert.equal(t.sent.at(-1).task_id, 'word-2');
}
{
    const t = setup(); t.client.receive(t.state); t.client.submit();
    const reload = setup(t.storage); reload.client.init(); reload.client.receive(reload.state);
    assert.deepEqual(reload.sent.at(-1), t.sent[0], 'refresh retries exact unacknowledged attempt');
    reload.client.receive({...reload.state, revision:1, performance:1, task_id:'word-2', answer_token:'attempt-2', reply_to:'attempt-1', rejected:'stale_attempt'});
    assert.equal(reload.client.pending, null, 'already accepted retry is acknowledged without local increment');
}
{
    const t = setup(); t.client.receive(t.state); t.offline(true); t.client.submit();
    assert.ok(t.client.pending, 'offline send retains pending answer');
    t.offline(false); t.retry(); assert.equal(t.sent.length, 1);
}
{
    const t = setup(); t.client.receive(t.state); t.offline(true); t.client.stop();
    assert.equal(t.client.stopping, true);
    t.offline(false); t.retry(); assert.deepEqual(t.sent[0], {stop_work: true});
    const reload = setup(t.storage); reload.client.init(); reload.client.receive(reload.state);
    assert.deepEqual(reload.sent.at(-1), {stop_work: true}, 'stop intent survives refresh');
    reload.client.receive({...reload.state, stopped_work:true, revision:1});
    assert.equal(reload.client.stopping, false); assert.equal(reload.storage.size, 0);
}
{
    const t = setup(); t.offline(true); t.client.init(); t.offline(false); t.retry();
    assert.deepEqual(t.sent[0], {init:true}, 'initial connection retries safely');
}
{
    const t = setup(); t.client.receive({...t.state, revision:2, performance:2});
    t.client.receive({...t.state, revision:1, performance:1});
    assert.equal(t.client.state.performance, 2, 'old replies cannot roll back newer state');
}
{
    const t = setup(); t.client.receive({...t.state, stopped_work:true}); t.client.submit();
    assert.equal(t.sent.length, 0, 'stopped client cannot submit another answer');
}
{
    const t = setup(); let callbackRan = false;
    t.client.options.onState = () => {
        assert.equal(t.busy.at(-1), false, 'inputs are re-enabled before page callback restores focus');
        callbackRan = true;
    };
    t.client.receive(t.state);
    assert.equal(callbackRan, true);
}
console.log('8 task-client scenarios passed: duplicate click, retry, refresh, offline answer/stop/init, stale reply, stopped state, focus callback order.');
