<p align="center">
  <img src="assets/hero-radar.svg" alt="Aykut Emre Yalcin - backend engineer" width="880">
</p>

<p align="center">
  <a href="https://aykutemreyalcin.com"><img alt="Personal site" src="https://img.shields.io/badge/aykutemreyalcin.com-1f2328?style=flat-square&logo=safari&logoColor=white"></a>
  <a href="https://fosapps.com"><img alt="Fos Apps" src="https://img.shields.io/badge/fosapps.com-4b91f1?style=flat-square&logo=shopify&logoColor=white"></a>
  <a href="https://enretag.com"><img alt="Enretag" src="https://img.shields.io/badge/enretag.com-bc4c00?style=flat-square&logo=fedex&logoColor=white"></a>
  <img alt="Warsaw" src="https://img.shields.io/badge/Warsaw-PL-6e7781?style=flat-square&logo=googlemaps&logoColor=white">
</p>

---

## whoami

I build the unglamorous machinery behind e-commerce: order pipelines, carrier integrations,
warehouse software and the Shopify tooling that sits on top of it. Most of my day is Java and
Spring talking to Postgres, queues and third-party APIs that were never designed to be talked to.

Before commerce I spent my time on the other side of the wire, writing scanners, sniffers and
rogue access points in Python. That habit never really left, and it shows up as a reflex to ask
what happens when a request is malformed, replayed or hostile.

- Backend engineer, currently deep in fulfillment and logistics systems
- Building [Fos Apps](https://fosapps.com), a set of five focused Shopify utilities
- Engineering the software behind [Enretag](https://enretag.com), a US fulfillment operation
- Long-running interest in aviation, which is where the radar above comes from

---

## Live systems

Every six hours a GitHub Action pings the things I run and redraws this board. No third-party
uptime service, just a Python script and a hand-drawn SVG. If something is red, it is genuinely
broken right now.

<p align="center">
  <img src="assets/status.svg" alt="Live status of aykutemreyalcin.com, fosapps.com and enretag.com" width="880">
</p>

---

## Recent transmissions

<!-- pulse:activity:start -->
- `  9d ago` merged pull request #10 in [`ata-rag-chat-fe`](https://github.com/aykutemreyalcin/ata-rag-chat-fe)
- `  9d ago` opened pull request #10 in [`ata-rag-chat-fe`](https://github.com/aykutemreyalcin/ata-rag-chat-fe)
- `  9d ago` created branch `fix/chat-feedback-pending` on [`ata-rag-chat-fe`](https://github.com/aykutemreyalcin/ata-rag-chat-fe)
- `  9d ago` merged pull request #4 in [`ata-rag-chat-be`](https://github.com/aykutemreyalcin/ata-rag-chat-be)
- `  9d ago` opened pull request #4 in [`ata-rag-chat-be`](https://github.com/aykutemreyalcin/ata-rag-chat-be)
<!-- pulse:activity:end -->

---

## How I build

The same shape shows up in almost everything I work on: pull orders from somewhere I do not
control, normalise them, make every step replayable, and never lose a package because a carrier
API returned a 500.

<p align="center">
  <img src="assets/pipeline.svg" alt="Order pipeline: sources, Spring API, queue, fulfillment, carriers" width="880">
</p>

<details>
<summary><b>The principles behind that diagram</b></summary>

<br>

```mermaid
flowchart LR
    A[External API<br/>I do not control] -->|tolerant parsing| B[Normalised domain model]
    B --> C{Is this idempotent?}
    C -->|no| D[Make it idempotent<br/>dedupe key + upsert]
    C -->|yes| E[Persist and enqueue]
    D --> E
    E --> F[Worker with bounded retries]
    F -->|success| G[Ship it]
    F -->|exhausted| H[Dead letter queue<br/>and alert a human]
```

- **Assume the upstream lies.** Third-party order and carrier APIs change shape without notice,
  so parsing is defensive and unknown fields never crash an import.
- **Every write is replayable.** Imports and label calls carry a dedupe key, because the honest
  answer to "did that request go through?" is usually "maybe".
- **Failures get a destination.** A job that cannot succeed lands somewhere a person will
  actually look, instead of disappearing into a log file.
- **Boring beats clever.** This code runs unattended while a warehouse depends on it.

</details>

---

## In transit

What I am actively working on, tracked the way I track everything else.

<p align="center">
  <img src="assets/tracking.svg" alt="Progress on active projects" width="880">
</p>

---

## Selected work

**Products**

| | |
|---|---|
| [**Fos&nbsp;Apps**](https://fosapps.com) | Five Shopify utilities: a product recycle bin, scheduled tag removal, serial number and warranty tracking, product change history, and quantity break discounts |
| [**Enretag**](https://enretag.com) | Fulfillment platform behind 1.5M+ shipped orders, with real-time tracking, inventory sync and multi-channel order intake |

**Repositories**

| | |
|---|---|
| [`ata-rag-chat-be`](https://github.com/aykutemreyalcin/ata-rag-chat-be) / [`fe`](https://github.com/aykutemreyalcin/ata-rag-chat-fe) | Retrieval-augmented chat, Java backend with a TypeScript client |
| [`internship_application_coordinator_be`](https://github.com/aykutemreyalcin/internship_application_coordinator_be) / [`fe`](https://github.com/aykutemreyalcin/internship_application_coordinator_fe) | Application tracking system, Spring plus TypeScript |
| [`repo_checker_be`](https://github.com/aykutemreyalcin/repo_checker_be) / [`fe`](https://github.com/aykutemreyalcin/repo_checker_fe) | GitHub repository inspector |
| [`ai_agent`](https://github.com/aykutemreyalcin/ai_agent) | Python agent runtime |
| [`boxMeter`](https://github.com/aykutemreyalcin/boxMeter) | Shopify app for parcel dimensioning |
| [`TorchLink`](https://github.com/aykutemreyalcin/TorchLink) | Swift iOS app |

<details>
<summary><b>Security toolkit</b> - the Python side of my brain</summary>

<br>

| | |
|---|---|
| [`Evil-Twin-Project`](https://github.com/aykutemreyalcin/Evil-Twin-Project) | Raspberry Pi rogue access point with client monitoring |
| [`mitm_ettercap`](https://github.com/aykutemreyalcin/mitm_ettercap) | Man-in-the-middle automation over nmap and ettercap |
| [`network_scanner`](https://github.com/aykutemreyalcin/network_scanner) | Network sweep for Linux |
| [`port_scanner`](https://github.com/aykutemreyalcin/port_scanner) | Threaded port scanner |
| [`self_packet_sniffer`](https://github.com/aykutemreyalcin/self_packet_sniffer) | Sniff your own traffic and see what leaks |
| [`Directory_Brute_forcer`](https://github.com/aykutemreyalcin/Directory_Brute_forcer) | Directory discovery tool |
| [`File_Encryptor`](https://github.com/aykutemreyalcin/File_Encryptor) | Symmetric file encryption |
| [`Bruteforce-sha-256`](https://github.com/aykutemreyalcin/Bruteforce-sha-256) | SHA-256 dictionary cracker |

Written to understand attacks, not to run them. Everything here targets hardware I own.

</details>

---

## Stack

**Backend**
![Java](https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![Spring](https://img.shields.io/badge/Spring-6DB33F?style=flat-square&logo=spring&logoColor=white)
![Postgres](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)

**Frontend**
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)

**Commerce**
![Shopify](https://img.shields.io/badge/Shopify-7AB55C?style=flat-square&logo=shopify&logoColor=white)
![GraphQL](https://img.shields.io/badge/GraphQL-E10098?style=flat-square&logo=graphql&logoColor=white)

**Platform**
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![Cloudflare](https://img.shields.io/badge/Cloudflare-F38020?style=flat-square&logo=cloudflare&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)

**Also**
![Swift](https://img.shields.io/badge/Swift-F05138?style=flat-square&logo=swift&logoColor=white)
![Wireshark](https://img.shields.io/badge/Wireshark-1679A7?style=flat-square&logo=wireshark&logoColor=white)

---

## Numbers

The usual hosted stat cards answer with 503s or twenty second timeouts often enough to show up
as a broken image, so this one is generated in this repository straight from the GitHub API.

<p align="center">
  <img src="assets/stats.svg" alt="Contributions, streaks and language mix" width="880">
</p>

---

## The snake still eats

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/aykutemreyalcin/aykutemreyalcin/output/snake-dark.svg">
    <img alt="Contribution snake" src="https://raw.githubusercontent.com/aykutemreyalcin/aykutemreyalcin/output/snake-light.svg" width="880">
  </picture>
</p>

---

<details>
<summary><b>Beyond the code</b></summary>

<br>

<!--
  Both widgets below are wired up but switched off until the accounts are connected.

  WakaTime : create an account at https://wakatime.com, install the editor plugin, then enable
             Settings > Account > "Display coding activity publicly". Uncomment the block and
             the card starts filling in on its own.

  Spotify  : visit https://spotify-github-profile.kittinan.vercel.app, authorise Spotify, copy
             the uid it hands back and paste it over SPOTIFY_UID below.

<img alt="Coding activity" src="https://github-readme-stats.vercel.app/api/wakatime?username=aykutemreyalcin&layout=compact&hide_border=true&theme=github_dark&bg_color=0d1117&title_color=64a1f4">

<a href="https://open.spotify.com/user/SPOTIFY_UID">
  <img alt="Now playing" src="https://spotify-github-profile.kittinan.vercel.app/api/view?uid=SPOTIFY_UID&cover_image=true&theme=novatorem&bar_color=39d353">
</a>
-->

Nothing connected yet.

</details>

---

## Reach me

- Site: [aykutemreyalcin.com](https://aykutemreyalcin.com)
- Products: [fosapps.com](https://fosapps.com) and [enretag.com](https://enretag.com)
- Open to interesting backend problems, especially the ones involving other people's APIs

<sub>The status board and activity log on this page rewrite themselves from GitHub Actions.
The radar, pipeline and tracking graphics are hand-written SVG, no generators involved.</sub>
