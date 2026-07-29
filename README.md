# Zellno Prison Bear

Zellno Prison Bear is a small config-only modification for DayZ that provides
an independent, resilient variant of the vanilla brown bear.

It was designed for controlled encounters, particularly around the Black
Market area on Prison Island in Chernarus.

## Classname

```text
Animal_UrsusArctos_ZellnoPrison
```

## Features

- Independent classname derived from `Animal_UrsusArctos`.
- Does not modify the vanilla bear globally.
- Vanilla model, textures, animations and sounds.
- Vanilla AI, movement, acceleration and attacks.
- Vanilla skinning resources and yields.
- Global Health: 15,000.
- Global Blood: 50,000.
- Global Shock: 5,000.
- No custom models, textures, sounds or third-party assets.
- Tested with DayZ 1.29 on Linux.

## Requirements

- DayZ.
- The mod must be loaded by both the server and connecting clients.

PvZmoD Spawn System is not a dependency. It was used during development only
as one possible method of creating controlled static spawns.

## Installation

Copy the compiled `@ZellnoPrisonBear` folder to the server and add it to the
client-visible `-mod` parameter.

Copy the included public key to the server keys directory.

Example:

```text
-mod="@OtherMods;@ZellnoPrisonBear"
```

## Usage

Spawn the following classname with VPPAdminTools, a mission script, an event
system or another compatible spawn system:

```text
Animal_UrsusArctos_ZellnoPrison
```

Static-spawn coordinates are intentionally not included. Navigation,
containment and balance depend on each server's buildings, map edits and
environment.

## Building

The included `build.sh` was developed for Linux using Wine and the official
DayZ Tools.

The build script expects the author's signing keys outside this repository.
Other developers should change the key paths or use their own signing process.

Compiled PBOs, signatures and signing keys are intentionally excluded from
the source repository.

## Local test installer

`install_local_test.py` documents the author's local Linux deployment workflow.
It is environment-specific, operates in simulation mode by default and
requires `--apply` before changing files.

Review and adapt every path before using it on another system.

## License

Original source code and documentation in this repository are licensed under
the MIT License.

DayZ, its assets and third-party modifications remain the property of their
respective rights holders. See [THIRD_PARTY.md](THIRD_PARTY.md).

## Disclaimer

This is an unofficial community modification for DayZ. It is not affiliated
with, authorized by, or endorsed by Bohemia Interactive a.s. DAYZ is a
registered trademark of Bohemia Interactive a.s.

## Monetization Permission

Zellno permits the use of Zellno Prison Bear on monetized DayZ servers,
provided that the server operator is registered, approved and listed under
Bohemia Interactive's DayZ Server Monetization program and complies with all
applicable rules.

This permission applies only to the original content provided by Zellno in
Zellno Prison Bear. It does not grant permission to monetize DayZ itself or
any third-party modification or content used alongside this mod.

Server operators are responsible for obtaining any additional permissions
required by the authors of other mods installed on their servers.

- [Official monetization rules](https://www.bohemia.net/monetization)
- [Approved DayZ servers](https://www.bohemia.net/monetization/approved/dayz)
