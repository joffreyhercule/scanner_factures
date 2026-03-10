# Routes API

Base URL : `http://localhost:8000`

Documentation interactive Swagger : `http://localhost:8000/docs`

## Clients

| Methode | Route | Description |
|---------|-------|-------------|
| GET | `/api/clients` | Liste tous les clients |
| GET | `/api/clients/{id}` | Detail d'un client |
| POST | `/api/clients` | Creer un client |
| PUT | `/api/clients/{id}` | Modifier un client |
| DELETE | `/api/clients/{id}` | Supprimer un client |

### Corps POST/PUT Client
```json
{
  "nom": "Dupont Jean",
  "adresse": "12 rue de la Paix, 75001 Paris",
  "telephone": "06 12 34 56 78",
  "email": "jean.dupont@email.fr"
}
```

## Vehicules

| Methode | Route | Description |
|---------|-------|-------------|
| GET | `/api/vehicules` | Liste tous les vehicules |
| GET | `/api/vehicules?client_id={id}` | Vehicules d'un client |
| GET | `/api/vehicules/{id}` | Detail d'un vehicule |
| POST | `/api/vehicules` | Creer un vehicule |
| PUT | `/api/vehicules/{id}` | Modifier un vehicule |
| DELETE | `/api/vehicules/{id}` | Supprimer un vehicule |

### Corps POST/PUT Vehicule
```json
{
  "client_id": "uuid-du-client",
  "marque": "Renault",
  "modele": "Clio",
  "immatriculation": "AB-123-CD",
  "vin": "VF1BB0G0654321098",
  "annee": 2020,
  "kilometrage": 85000
}
```

## Factures

| Methode | Route | Description |
|---------|-------|-------------|
| GET | `/api/factures` | Liste toutes les factures |
| GET | `/api/factures?client_id={id}` | Factures d'un client |
| GET | `/api/factures?vehicule_id={id}` | Factures d'un vehicule |
| GET | `/api/factures/stats` | Statistiques (CA HT, TVA, nb factures) |
| GET | `/api/factures/stats?client_id={id}` | Stats d'un client |
| GET | `/api/factures/{id}` | Detail d'une facture |
| POST | `/api/factures` | Creer une facture |
| PUT | `/api/factures/{id}` | Modifier une facture |
| DELETE | `/api/factures/{id}` | Supprimer une facture |

### Corps POST/PUT Facture
```json
{
  "numero_facture": "F-2024-001",
  "client_id": "uuid-du-client",
  "vehicule_id": "uuid-du-vehicule",
  "date_facture": "2024-03-15",
  "lignes": [
    {
      "description": "Vidange huile moteur",
      "quantite": 1,
      "prix_unitaire_ht": 45.00,
      "montant_ht": 45.00,
      "type": "main_oeuvre"
    },
    {
      "description": "Filtre a huile",
      "quantite": 1,
      "prix_unitaire_ht": 12.50,
      "montant_ht": 12.50,
      "type": "piece"
    }
  ],
  "total_ht": 57.50,
  "tva_taux": 20.0,
  "montant_tva": 11.50,
  "total_ttc": 69.00,
  "pdf_filename": "facture-001.pdf"
}
```

### Reponse GET /api/factures/stats
```json
{
  "nb_factures": 15,
  "total_ht": 4250.00,
  "total_tva": 850.00,
  "total_ttc": 5100.00
}
```

## Upload

| Methode | Route | Description |
|---------|-------|-------------|
| POST | `/api/upload` | Upload et traitement de fichiers PDF |

### Upload
- Content-Type : `multipart/form-data`
- Champ : `files` (un ou plusieurs fichiers PDF)

### Reponse Upload
```json
{
  "results": [
    {
      "status": "success",
      "action": "created",
      "facture_id": "uuid",
      "client_id": "uuid",
      "vehicule_id": "uuid",
      "pdf_filename": "facture-001.pdf"
    }
  ]
}
```
