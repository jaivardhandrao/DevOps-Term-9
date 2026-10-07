import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { request } from './api.js';
import './style.css';

const lanes = [{ value: 'todo', label: 'To do', symbol: '○' }, { value: 'in_progress', label: 'In progress', symbol: '◐' }, { value: 'done', label: 'Done', symbol: '●' }];
const blank = { title: '', description: '', status: 'todo', priority: 'medium' };
const date = value => new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });

function App() {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({ total: 0, todo: 0, in_progress: 0, done: 0 });
  const [search, setSearch] = useState('');
  const [priority, setPriority] = useState('all');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [editor, setEditor] = useState(null);
  const [notice, setNotice] = useState('');
  const [more, setMore] = useState(false);
  const dialog = useRef(null);

  async function refresh() {
    setLoading(true);
    setError('');
    try {
      const [nextTasks, nextStats] = await Promise.all([request('/api/tasks?limit=500'), request('/api/tasks/stats')]);
      setTasks(nextTasks); setStats(nextStats); setMore(nextStats.total > nextTasks.length);
    } catch (problem) { setError(problem.message); }
    finally { setLoading(false); }
  }
  useEffect(() => { refresh(); }, []);
  useEffect(() => { if (editor !== null && !dialog.current?.open) dialog.current?.showModal(); }, [editor]);

  function closeEditor() { dialog.current?.close(); setEditor(null); }
  async function save(event) {
    event.preventDefault();
    if (busy) return;
    setBusy(true); setError('');
    try {
      const { id, title, description, status, priority } = editor;
      await request(id ? `/api/tasks/${id}` : '/api/tasks', { method: id ? 'PUT' : 'POST', body: JSON.stringify({ title, description, status, priority }) });
      closeEditor(); setNotice(id ? 'Task updated.' : 'Task created.'); await refresh();
    } catch (problem) { setError(problem.message); }
    finally { setBusy(false); }
  }
  async function remove() {
    if (busy || !window.confirm('Delete this task? This cannot be undone.')) return;
    setBusy(true); setError('');
    try { await request(`/api/tasks/${editor.id}`, { method: 'DELETE' }); closeEditor(); setNotice('Task deleted.'); await refresh(); }
    catch (problem) { setError(problem.message); }
    finally { setBusy(false); }
  }
  function editField(field, value) { setEditor(current => ({ ...current, [field]: value })); }
  const visible = tasks.filter(task => (priority === 'all' || task.priority === priority) && `${task.title} ${task.description}`.toLowerCase().includes(search.toLowerCase()));
  const completion = stats.total ? Math.round(stats.done / stats.total * 100) : 0;

  return <div className="workspace">
    <aside className="rail">
      <a className="brand" href="#main"><span className="brand-mark" aria-hidden="true">▤</span>TaskBoard</a>
      <div className="workspace-name"><span className="avatar">TB</span><div>Team workspace<small>A little more organized.</small></div></div>
      <nav aria-label="Workspace"><a href="#main" className="nav-current"><span aria-hidden="true">▦</span> Project board <span>{stats.total}</span></a><a href="#progress"><span aria-hidden="true">◔</span> Progress</a></nav>
      <div className="rail-note"><span className="note-icon" aria-hidden="true">✦</span><strong>Make room for focus.</strong><p>Keep the next step clear. Move work forward one task at a time.</p></div>
      <footer><span className="avatar small">JD</span><span>Jaivardhan’s workspace<small>DevOps capstone</small></span></footer>
    </aside>
    <main id="main">
      <header className="topbar"><span>Workspace / Project board</span><button className="text-button" onClick={refresh} disabled={loading || busy} aria-label="Refresh board">↻ Refresh</button></header>
      <div className="page-content">
        <div className="heading"><div><h1>Good work starts here.</h1><p>A shared view of what’s next, what’s moving, and what’s done.</p></div><button className="primary" onClick={() => { setError(''); setEditor({ ...blank }); }}>＋ New task</button></div>
        <section id="progress" className="progress-strip" aria-label="Project progress">
          <div className="progress-summary"><div><span>Project progress</span><strong>{completion}<span>%</span></strong></div><div className="progress-track" role="progressbar" aria-label="Completed tasks" aria-valuenow={completion} aria-valuemin="0" aria-valuemax="100"><span style={{ width: `${completion}%` }}/></div><p>{stats.done} of {stats.total} tasks complete</p></div>
          {lanes.map(lane => <div className={`stat ${lane.value}`} key={lane.value}><span className="status-symbol" aria-hidden="true">{lane.symbol}</span><div><strong>{stats[lane.value]}</strong><span>{lane.label}</span></div></div>)}
        </section>
        <div className="board-heading"><div><h2>Project board</h2><span>{visible.length} visible tasks</span></div><div className="filters"><label className="search"><span aria-hidden="true">⌕</span><input aria-label="Search tasks" placeholder="Search tasks…" value={search} onChange={e => setSearch(e.target.value)}/></label><label className="priority-filter"><span className="sr-only">Filter priority</span><select value={priority} onChange={e => setPriority(e.target.value)}><option value="all">All priorities</option><option value="high">High priority</option><option value="medium">Medium priority</option><option value="low">Low priority</option></select></label></div></div>
        {error && editor === null && <div className="error" role="alert">{error} <button onClick={refresh}>Try again</button></div>}
        <p className="sr-only" role="status">{notice}</p>
        {more && <p className="message">Showing the newest 500 tasks. Project totals include all tasks.</p>}
        {loading && <p className="message" role="status">Loading your board…</p>}
        <section className="board" aria-label="Task board" aria-busy={loading}>
          {lanes.map(lane => <section className={`lane ${lane.value}`} key={lane.value} aria-label={lane.label}>
            <div className="lane-heading"><h3><span className="status-symbol" aria-hidden="true">{lane.symbol}</span>{lane.label}</h3><span>{visible.filter(t => t.status === lane.value).length}</span></div>
            <div className="task-list">{visible.filter(task => task.status === lane.value).map(task => <button className="task" key={task.id} onClick={() => { setError(''); setEditor(task); }} aria-label={`Edit ${task.title}`}>
              <div className="task-meta"><span>TB-{String(task.id).padStart(3, '0')}</span><span className={`priority ${task.priority}`}>{task.priority}</span></div>
              <h4>{task.title}</h4>{task.description && <p>{task.description}</p>}<div className="task-footer"><span>Updated {date(task.updated_at)}</span><span aria-hidden="true">↗</span></div>
            </button>)}</div>
            {!loading && !visible.some(task => task.status === lane.value) && <div className="empty"><span aria-hidden="true">{lane.symbol}</span><p>{search || priority !== 'all' ? 'No matching tasks.' : lane.value === 'todo' ? 'Your next idea goes here.' : lane.value === 'in_progress' ? 'Ready when you are.' : 'A home for finished work.'}</p></div>}
            <button className="add-task" onClick={() => { setError(''); setEditor({ ...blank, status: lane.value }); }}>＋ Add task</button>
          </section>)}
        </section>
        <footer className="board-footer"><span>Small steps. Shared progress.</span><span>Click a task to edit its details or status.</span></footer>
      </div>
    </main>
    <dialog ref={dialog} className="editor" onCancel={event => { if (busy) event.preventDefault(); else closeEditor(); }}>
      {editor && <form onSubmit={save}><div className="editor-heading"><div><span>{editor.id ? `TB-${String(editor.id).padStart(3, '0')}` : 'Project board'}</span><h2>{editor.id ? 'Task details' : 'Create a task'}</h2></div><button type="button" className="close" onClick={closeEditor} disabled={busy} aria-label="Close task editor">×</button></div>
        <label>Task title<input autoFocus required maxLength="160" value={editor.title} onChange={e => editField('title', e.target.value)} placeholder="What needs to happen?"/></label>
        <label>Description<textarea maxLength="5000" rows="4" value={editor.description} onChange={e => editField('description', e.target.value)} placeholder="Add the context someone needs to get started."/></label>
        <div className="form-row"><label>Status<select value={editor.status} onChange={e => editField('status', e.target.value)}>{lanes.map(lane => <option key={lane.value} value={lane.value}>{lane.label}</option>)}</select></label><label>Priority<select value={editor.priority} onChange={e => editField('priority', e.target.value)}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></label></div>
        {error && <p role="alert" className="error">{error}</p>}
        <div className="editor-actions">{editor.id && <button type="button" className="danger-button" onClick={remove} disabled={busy}>Delete task</button>}<button type="button" className="secondary" onClick={closeEditor} disabled={busy}>Cancel</button><button className="primary" disabled={busy || !editor.title.trim()}>{busy ? 'Saving…' : editor.id ? 'Save changes' : 'Create task'}</button></div>
      </form>}
    </dialog>
  </div>;
}

createRoot(document.getElementById('root')).render(<App/>);
