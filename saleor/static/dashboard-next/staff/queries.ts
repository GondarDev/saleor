import gql from "graphql-tag";
import { TypedQuery } from "../queries";
import { StaffList, StaffListVariables } from "./types/StaffList";
import {
  StaffMemberDetails,
  StaffMemberDetailsVariables
} from "./types/StaffMemberDetails";

export const staffMemberFragment = gql`
  fragment StaffMemberFragment on User {
    id
    email
    isActive
  }
`;
export const staffMemberDetailsFragment = gql`
  ${staffMemberFragment}
  fragment StaffMemberDetailsFragment on User {
    ...StaffMemberFragment
    permissions {
      code
      name
    }
  }
`;
const staffList = gql`
  ${staffMemberFragment}
  query StaffList($first: Int, $after: String, $last: Int, $before: String) {
    shop {
      permissions {
        code
        name
      }
    }
    staffUsers(before: $before, after: $after, first: $first, last: $last) {
      edges {
        cursor
        node {
          ...StaffMemberFragment
        }
      }
      pageInfo {
        hasPreviousPage
        hasNextPage
        startCursor
        endCursor
      }
    }
  }
`;
export const TypedStaffListQuery = TypedQuery<StaffList, StaffListVariables>(
  staffList
);

export const staffMemberDetails = gql`
  ${staffMemberDetailsFragment}
  query StaffMemberDetails($id: ID!) {
    user(id: $id) {
      ...StaffMemberDetailsFragment
    }
  }
`;
export const TypedOrderDetailsQuery = TypedQuery<
  StaffMemberDetails,
  StaffMemberDetailsVariables
>(staffMemberDetails);
