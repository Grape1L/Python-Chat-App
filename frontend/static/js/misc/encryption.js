const modulus =
    115792089237316195423570985008687907852837564279074904382605163141518161494337n;
const defaultBase = 9821379832032095782348677823478712n;

export function generatePrivateKey() {
    const bytes = new Uint8Array(20);
    crypto.getRandomValues(bytes);

    let key = 0n;
    for (const byte of bytes) {
        key = (key << 8n) + BigInt(byte);
    }
    return key;
}

export function calculateKey(privateKey, base = defaultBase) {
    base = BigInt(base) % modulus;
    let exp = BigInt(privateKey);

    let result = 1n;
    while (exp > 0n) {
        if (exp & 1n) result = (result * base) % modulus;

        base = (base * base) % modulus;
        exp >>= 1n;
    }

    return result;
}

export async function encryptData(data, key) {
    const encodedData = new TextEncoder().encode(data);

    const cryptoKey = await getKey(key);

    const iv = crypto.getRandomValues(new Uint8Array(12));

    const ciphertext = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv },
        cryptoKey,
        encodedData,
    );

    const result = new Uint8Array(iv.length + ciphertext.byteLength);
    result.set(iv, 0);
    result.set(new Uint8Array(ciphertext), iv.length);

    return btoa(String.fromCharCode(...result));
}

export async function decryptData(data, key) {
    const cryptoKey = await getKey(key);

    const bytes = Uint8Array.from(atob(data), (c) => c.charCodeAt(0));
    const iv = bytes.slice(0, 12);
    const ciphertext = bytes.slice(12);

    const decrypted = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv },
        cryptoKey,
        ciphertext,
    );

    return new TextDecoder().decode(decrypted);
}

async function getKey(key) {
    const enc = new TextEncoder();
    const keyData = enc.encode(String(key));

    return crypto.subtle.importKey(
        "raw",
        await crypto.subtle.digest("SHA-256", keyData),
        { name: "AES-GCM" },
        false,
        ["encrypt", "decrypt"],
    );
}
