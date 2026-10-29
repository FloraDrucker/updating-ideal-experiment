/* One outstanding server-checked answer. Retry the same token after a lost reply. */
class TaskClient {
    constructor(options) {
        this.options = options;
        this.state = null;
        this.pending = null;
        this.retry = null;
        this.stopping = false;
        try { this.pending = JSON.parse(sessionStorage.getItem(options.storageKey)); } catch (_) {}
        try { this.stopping = sessionStorage.getItem(options.storageKey + '_stop') === '1'; } catch (_) {}
    }
    save() {
        try {
            if (this.pending) sessionStorage.setItem(this.options.storageKey, JSON.stringify(this.pending));
            else sessionStorage.removeItem(this.options.storageKey);
        } catch (_) {}
    }
    init() {
        this.options.setBusy(true);
        try { liveSend({init: true}); } catch (_) { /* Retry when connection is ready. */ }
        clearTimeout(this.retry);
        this.retry = setTimeout(() => { if (!this.state) this.init(); }, 3000);
    }
    sendPending() {
        if (!this.pending) return;
        this.options.setBusy(true);
        try { liveSend(this.pending); } catch (_) { /* Keep the token for retry/reload. */ }
        clearTimeout(this.retry);
        this.retry = setTimeout(() => this.sendPending(), 3000);
    }
    submit() {
        if (this.pending || this.stopping || !this.state || this.state.completed || this.state.stopped_work) return;
        this.pending = {
            task_id: this.state.task_id,
            answer_token: this.state.answer_token,
            answer: this.options.getAnswer(),
        };
        this.save();
        this.sendPending();
    }
    stop() {
        if (this.pending || this.stopping || !this.state) return;
        this.stopping = true;
        try { sessionStorage.setItem(this.options.storageKey + '_stop', '1'); } catch (_) {}
        this.sendStop();
    }
    sendStop() {
        if (!this.stopping) return;
        this.options.setBusy(true);
        try { liveSend({stop_work: true}); } catch (_) { /* Retain stop intent for retry. */ }
        clearTimeout(this.retry);
        this.retry = setTimeout(() => this.sendStop(), 3000);
    }
    receive(data) {
        if (!data.task_id) return;
        if (this.state && data.revision < this.state.revision) return;
        clearTimeout(this.retry);
        const changedTask = !this.state || data.task_id !== this.state.task_id;
        if (this.pending && data.reply_to === this.pending.answer_token) {
            this.pending = null;
            this.save();
            clearTimeout(this.retry);
        }
        this.state = data;
        if (data.stopped_work || data.rejected === 'work_required') {
            this.stopping = false;
            clearTimeout(this.retry);
            try { sessionStorage.removeItem(this.options.storageKey + '_stop'); } catch (_) {}
        }
        this.options.setBusy(Boolean(this.pending) || this.stopping);
        this.options.onState(data, changedTask);
        // A reload first fetches server state, then retries the saved attempt.
        // If it was already accepted, the server returns a stale-attempt reply.
        if (this.pending) this.sendPending();
        else if (this.stopping) this.sendStop();
    }
}
