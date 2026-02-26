# Glossary

## PEET
PEET ist der KI-Assistent in SystemONE. Er unterstützt per Chat, greift auf Systemkontext zu und hilft bei Navigation sowie Wissensabfragen.

## SmartSortierer
SmartSortierer ist das Dokumentmodul von SystemONE. Es verarbeitet Uploads automatisiert und macht Inhalte strukturiert sowie semantisch durchsuchbar.

## RAG (Retrieval-Augmented Generation)
RAG kombiniert Dokumentensuche mit LLM-Antworten. Das Modell antwortet dabei auf Basis gefundener Inhalte statt nur aus seinem Grundwissen.

## Qdrant
Qdrant ist die Vektor-Datenbank für semantische Suche. Dort werden Embeddings von Dokument-Chunks gespeichert und abgefragt.

## Ollama
Ollama führt lokale KI-Modelle aus (z. B. Chat und Embeddings). Dadurch bleiben Daten und Inferenz lokal kontrollierbar.

## Worker
Der Worker verarbeitet Hintergrundjobs asynchron (z. B. OCR, Chunking, Embeddings). Dadurch bleibt die API schnell und stabil.

## Reverse Proxy
Ein Reverse Proxy (hier NGINX) ist der zentrale Eingangspunkt für HTTP-Anfragen. Er übernimmt Routing, optionale TLS-Terminierung und Sicherheitsregeln.

## Local-first
Local-first bedeutet: Dienste und Daten laufen primär lokal statt in der Cloud. Das verbessert Datenschutz, Unabhängigkeit und Kontrolle.

## Exo-node
Ein exo-node ist ein leichter Zusatzknoten (z. B. Mac mini) für UI-nahe oder weniger rechenintensive Aufgaben im verteilten Setup.
