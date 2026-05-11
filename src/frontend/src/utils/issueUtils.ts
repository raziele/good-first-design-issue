/**
 * RULE-ISS-002: Description truncation utility.
 */

const MAX_DESCRIPTION_LENGTH = 200;

export function truncateDescription(description: string): string {
  if (description.length <= MAX_DESCRIPTION_LENGTH) {
    return description;
  }
  return description.slice(0, MAX_DESCRIPTION_LENGTH - 3) + "...";
}
