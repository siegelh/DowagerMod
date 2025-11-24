import { GitHubBranch, REPO_OWNER, REPO_NAME } from '../types';

export const fetchBranches = async (): Promise<GitHubBranch[]> => {
  try {
    const response = await fetch(`https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/branches`);
    
    if (!response.ok) {
      throw new Error(`GitHub API Error: ${response.statusText}`);
    }
    
    const branches: GitHubBranch[] = await response.json();
    
    // Fetch commit details for each branch to get the date
    // We fetch in parallel to speed up the process
    const branchesWithDates = await Promise.all(
      branches.map(async (branch) => {
        try {
          const commitResponse = await fetch(branch.commit.url);
          if (commitResponse.ok) {
            const commitData = await commitResponse.json();
            return {
              ...branch,
              lastUpdated: commitData.commit.committer.date
            };
          }
        } catch (err) {
          console.warn(`Could not fetch details for branch ${branch.name}`, err);
        }
        return branch;
      })
    );

    // Sort by lastUpdated descending (newest first)
    return branchesWithDates.sort((a, b) => {
      const dateA = a.lastUpdated ? new Date(a.lastUpdated).getTime() : 0;
      const dateB = b.lastUpdated ? new Date(b.lastUpdated).getTime() : 0;
      return dateB - dateA;
    });

  } catch (error) {
    console.error("Failed to fetch branches", error);
    throw error;
  }
};