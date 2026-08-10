# Workspace v0.55.0 — API & Embed Foundation

v0.55.0 establishes a stable read-only integration boundary without converting browser-local Workspace research into a server database.

## Durable references

Canonical Integrated Knowledge records may be identified with a stable URI:

`scw://project/{project-id}/{kind}/{record-id}`

The URI is an identifier only. It is not an access token, authorization grant, authentication assertion, or public URL.

## Explicit read-only projections

Workspace data remains private/browser-local by default. A user may deliberately create a `sc-workspace-readonly-projection/1.0` package for one selected canonical record. The projection always exposes its title and stable identity, while summary, tags, recorded provenance, and full content are separately selectable disclosure fields.

Creating a projection does not upload it. The projection is stored browser-locally until it is explicitly exported or copied into an embed.

## Static API envelope

The v1 API envelope is a portable JSON representation of an explicit projection. It is read-only and static. v0.55.0 does not expose a server route that can enumerate or retrieve private projects or project objects.

The public WordPress REST route `/wp-json/sc-workspace/v1/api-embed-contract` describes the contract and renderer only. It does not return user research.

## Embeds

A static embed includes the explicit projection payload and the public renderer script. The renderer performs no live project fetch and renders text using DOM text nodes rather than HTML injection.

## Boundary

- Storage 35 and Project 20.0 remain unchanged.
- No live server project API.
- No project discovery endpoint.
- No automatic publication or refresh.
- No canonical mutation from API/embed surfaces.
- Projection fingerprints are integrity receipts, not signatures or authorization.
- The 4px Workspace editorial header rule remains unchanged.
