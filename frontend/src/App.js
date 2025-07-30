/*  src/App.js  – upload success toast + icons fixed at bottom  */
import React, { useState, useRef, useEffect } from "react";
import {
	LiveKitRoom,
	RoomAudioRenderer,
	StartAudio,
	useRoomContext,
} from "@livekit/components-react";
import { RoomEvent } from "livekit-client";
import clsx from "clsx";
import "./App.css";
import "@livekit/components-styles";

/* access key from .env */
const SHA_KEY = process.env.REACT_APP_SHA_KEY ?? "";

export default function App() {
	/* ----- state ----- */
	const [token, setToken] = useState(null);
	const [joined, setJoined] = useState(false);
	const [roomName, setRoom] = useState("");
	const [toast, setToast] = useState({ text: "", type: "" });
	const [log, setLog] = useState([]);
	const [access, setAccess] = useState("");
	const fileRef = useRef();

	/* ----- toast helper ----- */
	const showToast = (text, type = "error") => {
		setToast({ text, type });
		setTimeout(() => setToast({ text: "", type: "" }), 2500);
	};

	/* ----- join ----- */
	async function startCall() {
		if (access.trim() !== SHA_KEY) {
			showToast("Invalid access key");
			return;
		}
		try {
			const room = `quark-${Date.now()}`;
			const identity = `browser-${Math.random().toString(36).slice(2, 10)}`;
			const r = await fetch(`/api/getToken?room=${room}&identity=${identity}`);
			if (!r.ok) throw new Error("token fetch failed");
			setToken((await r.json()).token);
			setRoom(room);
			setJoined(true);
		} catch (e) {
			showToast(e.message);
		}
	}

	/* ----- upload ----- */
	async function onUpload(e) {
		const f = e.target.files?.[0];
		if (!f) return;
		const form = new FormData();
		form.append("file", f);
		const res = await fetch("/api/upload", { method: "POST", body: form });
		if (res.ok) showToast(`Uploaded ${f.name}`, "success");
		else showToast("Upload failed");
		fileRef.current.value = "";
	}

	/* ----- download ----- */
	function downloadTxt() {
		const txt = log.map((l) => `${l.who}: ${l.text}`).join("\n");
		const blob = new Blob([txt], { type: "text/plain" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = "transcript.txt";
		a.click();
		URL.revokeObjectURL(url);
	}

	const hangup = () => {
		setJoined(false);
		setToken(null);
		setRoom("");
		setLog([]);
		setAccess("");
	};

	return (
		<main className={clsx("stage", joined && "talk")}>
			{toast.text && (
				<div className={clsx("toast", toast.type)}>{toast.text}</div>
			)}

			{/* --- landing gate --- */}
			{!joined
				? <div className="gate">
						<input
							className="keyInput"
							type="password"
							placeholder="Enter access key"
							value={access}
							onChange={(e) => setAccess(e.target.value)}
						/>
						<button className="ball start" onClick={startCall}>
							<span>Start Call</span>
						</button>
					</div>
				: <>
						<p className="roomLabel">{roomName}</p>

						<LiveKitRoom
							serverUrl={process.env.REACT_APP_LIVEKIT_URL}
							token={token}
							connect={true}
							audio={true}
							video={false}
							autoSubscribe={true}
							onDisconnected={hangup}
							className="room"
							data-lk-theme="default"
						>
							<RoomAudioRenderer />
							<StartAudio label="Click to enable audio" />

							<Avatar />
							<Transcript log={log} setLog={setLog} />

							{/* --- icons pinned near bottom --- */}
							<div className="bottomBtns fixedBottom">
								<label className="upload">
									📎
									<input
										hidden
										type="file"
										accept=".pdf"
										ref={fileRef}
										onChange={onUpload}
									/>
								</label>
								<button
									className="download"
									onClick={downloadTxt}
									title="Download transcript"
								>
									⤓
								</button>
							</div>

							<Toolbar onHangup={hangup} />
						</LiveKitRoom>
					</>}
		</main>
	);
}

/* ---------- TOOLBAR ---------- */
function Toolbar({ onHangup }) {
	const room = useRoomContext();
	return (
		<div className="toolbar">
			<button
				onClick={async () => {
					await room.disconnect();
					onHangup();
				}}
			>
				End Call
			</button>
		</div>
	);
}

/* ---------- TRANSCRIPT ---------- */
function Transcript({ log, setLog }) {
	const room = useRoomContext();
	const end = useRef();

	useEffect(() => {
		const unreg = room.registerTextStreamHandler(
			"lk.transcription",
			async (r, i) => {
				const text = (await r.readAll()).trim();
				const who = i.identity.includes("agent") ? "Harry" : "You";
				setLog((lines) => {
					const last = [...lines].reverse().find((l) => l.who === who);
					if (last && last.text === text) return lines;
					return [...lines, { who, text }];
				});
			},
		);
		return () => unreg?.();
	}, [room, setLog]);

	useEffect(() => end.current?.scrollIntoView({ behavior: "smooth" }), [log]);

	const display = (() => {
		const out = [];
		for (let i = log.length - 1; i >= 0 && out.length < 2; --i)
			if (out.every((l) => l.who !== log[i].who)) out.push(log[i]);
		return out.reverse();
	})();

	return (
		<div className="scroll">
			{display.map((l, i) => (
				<p key={i}>
					<strong>{l.who}: </strong>
					{l.text}
				</p>
			))}
			<div ref={end} />
		</div>
	);
}

/* ---------- AVATAR ---------- */
function Avatar() {
	const room = useRoomContext();
	const localId = room?.localParticipant?.identity;
	const [speaking, setSpeaking] = useState(false);

	useEffect(() => {
		if (!room) return;
		const up = () =>
			setSpeaking(room.activeSpeakers.some((p) => p.identity !== localId));
		room.on(RoomEvent.ActiveSpeakersChanged, up);
		up();
		return () => room.off(RoomEvent.ActiveSpeakersChanged, up);
	}, [room, localId]);

	return (
		<div className="avatarWrapper">
			<div className={clsx("ball pulse", !speaking && "idle")} />
		</div>
	);
}
