def create_sample_lead(client):
    return client.post(
        "/api/v1/leads",
        data={
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
        },
        files={
            "resume": ("resume.pdf", b"%PDF-1.4 sample", "application/pdf"),
        },
    )


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_lead(client):
    response = create_sample_lead(client)
    assert response.status_code == 201
    assert response.json()["status"] == "PENDING"


def test_protected_leads_require_auth(client):
    response = client.get("/api/v1/leads")
    assert response.status_code == 401


def test_admin_can_list_and_update_lead(client, auth_headers):
    created = create_sample_lead(client)
    lead_id = created.json()["id"]

    listed = client.get("/api/v1/leads", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.patch(
        f"/api/v1/leads/{lead_id}/status",
        headers=auth_headers,
        json={"status": "REACHED_OUT"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "REACHED_OUT"

    reverse = client.patch(
        f"/api/v1/leads/{lead_id}/status",
        headers=auth_headers,
        json={"status": "PENDING"},
    )
    assert reverse.status_code == 409
