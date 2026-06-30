export class MemoryAgent {
  private lastMessages: Map<string, number>;
  private timeoutMs: number;

  constructor(timeoutMs: number = 5000) {
    this.lastMessages = new Map();
    this.timeoutMs = timeoutMs;
  }

  /**
   * Vérifie si le message doit être prononcé (évite les répétitions)
   */
  public shouldSpeak(message: string): boolean {
    const now = Date.now();
    if (this.lastMessages.has(message)) {
      const lastTime = this.lastMessages.get(message)!;
      if (now - lastTime < this.timeoutMs) {
        return false; // Trop récent, on ignore
      }
    }
    
    // Mettre à jour la mémoire
    this.lastMessages.set(message, now);
    return true;
  }
}
