class Certificate:
    def __init__(self, name, serial_number, key_type, domains, expiry_date, certificate_path, private_key_path, status):
        self.name = name
        self.serial_number = serial_number
        self.key_type = key_type
        self.domains = domains
        self.expiry_date = expiry_date
        self.certificate_path = certificate_path
        self.private_key_path = private_key_path
        self.status = status

    def __repr__(self):
        return f"Certificate(name={self.name}, domains={self.domains}, expiry_date={self.expiry_date}, status={self.status})"


def parse_certificates(file_path):
    """Parse certificates from the input file and return a list of Certificate objects."""
    certificates = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

    current_cert = {}
    for line in lines:
        line = line.strip()
        if line.startswith("Certificate Name:"):
            if current_cert:
                certificates.append(Certificate(**current_cert))
                current_cert = {}
            current_cert['name'] = line.split(": ", 1)[1]
        elif line.startswith("Serial Number:"):
            current_cert['serial_number'] = line.split(": ", 1)[1]
        elif line.startswith("Key Type:"):
            current_cert['key_type'] = line.split(": ", 1)[1]
        elif line.startswith("Domains:"):
            current_cert['domains'] = line.split(": ", 1)[1]
        elif line.startswith("Expiry Date:"):
            expiry_info = line.split(": ", 1)[1]
            current_cert['expiry_date'] = expiry_info.split(" (")[0]
            current_cert['status'] = expiry_info.split(" (")[1].strip(")")
        elif line.startswith("Certificate Path:"):
            current_cert['certificate_path'] = line.split(": ", 1)[1]
        elif line.startswith("Private Key Path:"):
            current_cert['private_key_path'] = line.split(": ", 1)[1]

    if current_cert:
        certificates.append(Certificate(**current_cert))

    return certificates

def format_certificates_as_html_table(certificates):
    """
    Formats a list of certificates into an HTML table.

    Args:
        certificates (list): List of Certificate objects.

    Returns:
        str: A string representing the certificates in an HTML table format.
    """
    table_rows = ""
    for cert in certificates:
        table_rows += f"""
        <tr>
            <td>{cert.name}</td>
            <td>{cert.expiry_date}</td>
            <td>{cert.status}</td>
            <td>{cert.domains}</td>
        </tr>
        """

    html_table = f"""
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr>
                <th>Name</th>
                <th>Expiry Date</th>
                <th>Status</th>
                <th>Domains</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    """
    return html_table